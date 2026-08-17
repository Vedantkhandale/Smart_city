import math
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

import cv2
import numpy as np
import requests
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
DATABASE_PATH = os.path.join(BASE_DIR, "nagpur_pulse.db")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
IST = timezone(timedelta(hours=5, minutes=30))

app = Flask(__name__)
app.config.update(UPLOAD_FOLDER=UPLOAD_DIR, MAX_CONTENT_LENGTH=12 * 1024 * 1024)
# Needed for session-based Command Center auth. Set FLASK_SECRET_KEY in real deployments.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nagpur-pulse-hackathon-demo-key")
socketio = SocketIO(
    app,
    async_mode="threading",
    cors_allowed_origins=os.getenv("SOCKETIO_CORS_ORIGINS", "*"),
)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔐 Command Center demo credentials (hackathon-only — swap for a real user table / SSO later).
# Format: username -> {"password": ..., "display_name": ..., "department": ..., "role": ...}
COMMAND_CENTER_USERS = {
    # Admin - sees everything
    "admin": {"password": os.getenv("ADMIN_PASSWORD", "pulse2026"), "display_name": "Admin", "department": "All", "role": "admin"},
    
    # Department Heads
    "traffic_lead": {"password": "traffic123", "display_name": "Traffic Police Lead", "department": "Traffic", "role": "lead"},
    "pwd_chief": {"password": "pwd456", "display_name": "PWD Roads Chief", "department": "PWD", "role": "lead"},
    "water_lead": {"password": "water789", "display_name": "Water Works Lead", "department": "Water", "role": "lead"},
    "sanitation_lead": {"password": "sanitation321", "display_name": "Sanitation Lead", "department": "Sanitation", "role": "lead"},
    "infra_lead": {"password": "infra654", "display_name": "Infrastructure Lead", "department": "Infrastructure", "role": "lead"},
}

# ✨ Enhanced category configuration with detailed issue types
CATEGORY_CONFIG = {
    "Traffic": {
        "department": "Traffic Police",
        "sla": {"Critical": 20, "High": 45, "Medium": 120, "Low": 360},
        "signal": "road occupancy / signal obstruction",
        "issues": ["Signal fault", "Traffic jam", "Parking violation", "Rash driving", "Accident"]
    },
    "PWD": {
        "department": "PWD Roads",
        "sla": {"Critical": 45, "High": 90, "Medium": 240, "Low": 480},
        "signal": "surface discontinuity / road damage",
        "issues": ["Pothole", "Road crack", "Missing manhole cover", "Uneven surface", "Shoulder erosion"]
    },
    "Sanitation": {
        "department": "Solid Waste Management",
        "sla": {"Critical": 60, "High": 180, "Medium": 360, "Low": 720},
        "signal": "waste accumulation / hygiene risk",
        "issues": ["Garbage pile", "Illegal dumping", "Street cleaning needed", "Dead animal", "Drain blockage"]
    },
    "Water": {
        "department": "Water Works & Drainage",
        "sla": {"Critical": 30, "High": 90, "Medium": 240, "Low": 480},
        "signal": "water leak / drainage obstruction",
        "issues": ["Water leak", "Flooding", "Drain damaged", "Stagnant water", "Broken pipe"]
    },
    "Infrastructure": {
        "department": "Municipal Corporation",
        "sla": {"Critical": 25, "High": 60, "Medium": 180, "Low": 360},
        "signal": "street infrastructure damage",
        "issues": ["Street light broken", "Broken bench", "Fallen tree", "Damaged sign", "Pole damage"]
    }
}

NAGPUR_ZONES = [
    "Dharampeth Zone-1",
    "Dhantoli Zone-2",
    "Laxmi Nagar Zone-3",
    "Nehru Nagar Zone-4",
]


def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL UNIQUE,
                lat REAL NOT NULL, lng REAL NOT NULL, category TEXT NOT NULL,
                department TEXT NOT NULL, zone TEXT NOT NULL, severity TEXT NOT NULL,
                risk_score INTEGER NOT NULL, confidence INTEGER NOT NULL, quality_score INTEGER NOT NULL,
                detected_features INTEGER NOT NULL, visual_signal TEXT NOT NULL, ai_summary TEXT NOT NULL,
                voice TEXT NOT NULL, status TEXT NOT NULL, sla_minutes INTEGER NOT NULL,
                eta TEXT NOT NULL, image_url TEXT NOT NULL, duplicate_of TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_complaints_filters ON complaints(zone, category, status)")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_nagpur_zone(lat, lng):
    """Pragmatic demo zone classifier calibrated around Nagpur civic zones."""
    if lat >= 21.151:
        return "Dharampeth Zone-1"
    if lat >= 21.131:
        return "Dhantoli Zone-2"
    if lat >= 21.111:
        return "Laxmi Nagar Zone-3"
    return "Nehru Nagar Zone-4"


def clamp(value, low, high):
    return max(low, min(high, value))


def detect_issue_features(image, category):
    """🤖 Enhanced feature detection to identify specific issue types"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    features = {"detected": [], "confidence": {}}

    # Detect dark patches (street lights, broken fixtures)
    if category in {"Infrastructure", "PWD"}:
        dark_threshold = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(dark_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dark_patches = [c for c in contours if 500 < cv2.contourArea(c) < 50000]
        if len(dark_patches) > 0:
            features["detected"].append("Dark fixture detected (possible broken light)")
            features["confidence"]["street_light"] = min(75 + len(dark_patches) * 5, 95)

    # Detect horizontal lines (road damage, potholes)
    if category in {"PWD", "Sanitation"}:
        edges = cv2.Canny(gray, 65, 155)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=30, maxLineGap=10)
        if lines is not None and len(lines) > 5:
            features["detected"].append("Linear damage patterns detected")
            features["confidence"]["pothole"] = min(60 + len(lines) * 2, 90)

    # Detect debris/garbage (waste accumulation)
    if category in {"Sanitation", "Water"}:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_brown = np.array([10, 30, 30])
        upper_brown = np.array([25, 200, 200])
        mask = cv2.inRange(hsv, lower_brown, upper_brown)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        waste_contours = [c for c in contours if cv2.contourArea(c) > 100]
        if len(waste_contours) > 3:
            features["detected"].append("Waste/debris accumulation detected")
            features["confidence"]["garbage"] = min(70 + len(waste_contours), 92)

    return features


def analyze_civic_image(image_path, category):
    """🔍 Enhanced lightweight explainable computer-vision triage with AI filtering"""
    image = cv2.imread(image_path)
    if image is None:
        return {"status": "Rejected", "reason": "This file could not be read as an image."}

    height, width = image.shape[:2]
    if min(height, width) < 180:
        return {"status": "Rejected", "reason": "Image is too small for reliable civic triage. Please retake it closer to the issue."}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    edges = cv2.Canny(gray, 65, 155)
    edge_density = float(np.count_nonzero(edges)) / edges.size
    if blur_variance < 14:
        return {"status": "Rejected", "reason": "Image looks out of focus. A sharp frame helps the AI route it correctly.", "quality_score": round(clamp(blur_variance * 2, 0, 100))}
    if brightness < 18:
        return {"status": "Rejected", "reason": "Image is too dark to verify. Turn on flash or capture under a street light.", "quality_score": 12}

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    adaptive = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 7)
    contours, _ = cv2.findContours(adaptive, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    feature_count = len([c for c in contours if cv2.contourArea(c) > 40])

    ai_features = detect_issue_features(image, category)
    feature_boost = max(ai_features["confidence"].values()) if ai_features["confidence"] else 0

    category_weight = {"Traffic": 1.35, "PWD": 1.15, "Sanitation": 1.0, "Water": 1.22, "Infrastructure": 1.1}.get(category, 1.0)
    visual_risk = (edge_density * 430) + min(feature_count, 42) * 1.45 + contrast * 0.48
    risk_score = int(round(clamp(visual_risk * category_weight, 18, 98)))
    severity = "Critical" if risk_score >= 78 else "High" if risk_score >= 60 else "Medium" if risk_score >= 40 else "Low"
    focus_score = clamp(blur_variance / 3.2, 20, 100)
    exposure_score = 100 - min(abs(brightness - 128) * 0.55, 45)
    quality_score = int(round(clamp(focus_score * 0.62 + exposure_score * 0.38, 25, 99)))

    base_confidence = clamp(58 + quality_score * 0.25 + min(feature_count, 30) * 0.55, 62, 96)
    confidence = int(round(min(base_confidence + (feature_boost * 0.15), 96)))

    signal = CATEGORY_CONFIG[category]["signal"]
    feature_summary = " ".join(ai_features["detected"]) if ai_features["detected"] else ""
    full_summary = f"Vision triage found {feature_count} meaningful visual regions and a {risk_score}/100 risk pattern consistent with {signal}."
    if feature_summary:
        full_summary += f" {feature_summary}"

    return {
        "status": "Accepted", "severity": severity, "risk_score": risk_score,
        "confidence": confidence, "quality_score": quality_score, "features_detected": feature_count,
        "visual_signal": signal,
        "summary": full_summary,
        "ai_detected": ai_features["detected"],
        "measurements": {"focus": round(blur_variance, 1), "visual_density": round(edge_density * 100, 1), "exposure": round(brightness, 0)},
    }


def haversine_meters(lat_one, lng_one, lat_two, lng_two):
    radius = 6_371_000
    phi_one, phi_two = math.radians(lat_one), math.radians(lat_two)
    delta_phi, delta_lambda = math.radians(lat_two - lat_one), math.radians(lng_two - lng_one)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi_one) * math.cos(phi_two) * math.sin(delta_lambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_duplicate(lat, lng, category):
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=12)).replace(microsecond=0).isoformat()
    with get_db() as db:
        candidates = db.execute("SELECT reference, lat, lng FROM complaints WHERE category = ? AND created_at >= ?", (category, cutoff)).fetchall()
    for candidate in candidates:
        distance = haversine_meters(lat, lng, candidate["lat"], candidate["lng"])
        if distance <= 180:
            return {"reference": candidate["reference"], "distance": round(distance)}
    return None


def serialize_ticket(ticket):
    if not ticket:
        return {}
    data = dict(ticket)
    status = data.get("status") or "Queued"
    data["status_label"] = status
    data["is_rejected"] = status == "Rejected"
    data["is_resolved"] = status in {"Resolved", "Closed"}
    data["timeline"] = [
        {"label": "Submitted", "done": True, "time": data.get("created_at")},
        {"label": "Verified", "done": status in {"Queued", "Priority Dispatch", "Assigned", "In Progress", "Resolved", "Closed", "Rejected"}, "time": data.get("updated_at")},
        {"label": "Assigned", "done": status in {"Assigned", "In Progress", "Resolved", "Closed", "Rejected"}, "time": data.get("updated_at")},
        {"label": "In Progress", "done": status in {"In Progress", "Resolved", "Closed", "Rejected"}, "time": data.get("updated_at")},
        {"label": "Resolved", "done": status in {"Resolved", "Closed"}, "time": data.get("updated_at")},
    ]
    data["tracking_note"] = (
        "Rejected by civic operations." if status == "Rejected"
        else f"Current stage: {status}. Response target {data.get('eta', '—')}"
    )
    return data


def broadcast_ticket_event(event_name, ticket):
    """Pushes a small event payload to every connected command-center client."""
    socketio.emit(event_name, {"ticket": ticket, "emitted_at": utcnow()}, namespace="/")


def department_recipient(category):
    key = f"WHATSAPP_RECIPIENT_{category.upper()}"
    return os.getenv(key) or os.getenv("WHATSAPP_RECIPIENT")


def send_whatsapp_notification(ticket):
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    recipient = department_recipient(ticket["category"])
    if not all((access_token, phone_number_id, recipient)):
        return {"status": "not_configured", "detail": "Set WhatsApp environment variables to enable dispatch."}

    api_version = os.getenv("WHATSAPP_GRAPH_API_VERSION", "v23.0")
    endpoint = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    alert_text = (
        f"Nagpur Pulse alert: {ticket['severity']} {ticket['category']} report "
        f"{ticket['reference']} in {ticket['zone']}. Risk {ticket['risk_score']}/100. "
        f"Target response: {ticket['eta']}."
    )
    template_name = os.getenv("WHATSAPP_TEMPLATE_NAME")
    if template_name:
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": os.getenv("WHATSAPP_TEMPLATE_LANGUAGE", "en_US")},
                "components": [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": ticket["reference"]},
                        {"type": "text", "text": ticket["severity"]},
                        {"type": "text", "text": ticket["zone"]},
                    ],
                }],
            },
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": alert_text},
        }

    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
            timeout=10,
        )
        response_payload = response.json() if response.content else {}
    except requests.RequestException:
        return {"status": "failed", "detail": "Meta Cloud API did not respond; the ticket is still queued."}
    except ValueError:
        response_payload = {}

    if response.ok:
        messages = response_payload.get("messages", [])
        return {"status": "sent", "message_id": messages[0].get("id") if messages else None}
    return {
        "status": "failed",
        "detail": response_payload.get("error", {}).get("message", "Meta Cloud API rejected the dispatch."),
    }


def build_predictive_signals():
    """Explainable 2-hour risk forecast driven by current verified ticket density."""
    with get_db() as db:
        rows = db.execute("""
            SELECT zone, category, severity, risk_score
            FROM complaints
            WHERE status NOT IN ('Resolved', 'Closed')
        """).fetchall()

    zones = {zone: {"zone": zone, "active": 0, "urgent": 0, "risk_total": 0, "categories": {}} for zone in NAGPUR_ZONES}
    for row in rows:
        zone = zones.setdefault(row["zone"], {"zone": row["zone"], "active": 0, "urgent": 0, "risk_total": 0, "categories": {}})
        zone["active"] += 1
        zone["urgent"] += int(row["severity"] in {"Critical", "High"})
        zone["risk_total"] += row["risk_score"]
        zone["categories"][row["category"]] = zone["categories"].get(row["category"], 0) + 1

    forecast = []
    for zone in zones.values():
        average_risk = round(zone["risk_total"] / zone["active"]) if zone["active"] else 0
        score = int(clamp(12 + zone["active"] * 7 + zone["urgent"] * 15 + average_risk * 0.42, 8, 98))
        level = "Critical" if score >= 75 else "Elevated" if score >= 48 else "Stable"
        lead_category = max(zone["categories"], key=zone["categories"].get, default="No active signals")
        forecast.append({
            "zone": zone["zone"],
            "forecast_score": score,
            "level": level,
            "active": zone["active"],
            "urgent": zone["urgent"],
            "lead_category": lead_category,
            "confidence": min(96, 72 + zone["active"] * 5 + zone["urgent"] * 3),
            "window": "next 2 hours",
        })
    return sorted(forecast, key=lambda item: item["forecast_score"], reverse=True)


# ---------------------------------------------------------------------------
# 🔐 Command Center auth (hackathon-simple session auth — swap for real auth later)
# ---------------------------------------------------------------------------

def ensure_demo_session():
    if session.get("np_user"):
        return
    session["np_user"] = "admin"
    session["np_department"] = "All"
    session["np_role"] = "admin"


def login_required(view_fn):
    @wraps(view_fn)
    def wrapped(*args, **kwargs):
        ensure_demo_session()
        return view_fn(*args, **kwargs)
    return wrapped


def user_dashboard_route(username=None):
    user = COMMAND_CENTER_USERS.get(username or session.get("np_user"), {})
    if user.get("role") == "admin":
        return "admin_dashboard"
    department = user.get("department")
    mapping = {
        "Traffic": "traffic_dashboard",
        "PWD": "pwd_dashboard",
        "Water": "water_dashboard",
        "Sanitation": "sanitation_dashboard",
        "Infrastructure": "infrastructure_dashboard",
    }
    return mapping.get(department, "admin_dashboard")


@app.route("/login")
def login_page():
    if session.get("np_user"):
        return redirect(url_for(user_dashboard_route()))
    ensure_demo_session()
    return redirect(url_for("admin_dashboard"))


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    user = COMMAND_CENTER_USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid username or password."}), 401
    session["np_user"] = username
    session["np_department"] = user.get("department", "All")
    session["np_role"] = user.get("role", "staff")
    if payload.get("remember"):
        session.permanent = True
    return jsonify({"message": "Signed in.", "username": user["display_name"], "department": user.get("department", "All"), "role": user.get("role", "staff")})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.pop("np_user", None)
    session.pop("np_department", None)
    session.pop("np_role", None)
    return jsonify({"message": "Signed out."})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
@login_required
def admin_dashboard():
    ensure_demo_session()
    if session.get("np_user") and session.get("np_role") != "admin":
        route = user_dashboard_route(session.get("np_user"))
        return redirect(url_for(route))
    return render_template("admin_dashboard.html")


@app.route("/admin/access")
@login_required
def admin_department_access():
    ensure_demo_session()
    departments = [
        {"name": "Traffic", "route": "/dashboard/traffic", "icon": "🚗", "summary": "Signal, traffic flow and mobility incidents"},
        {"name": "PWD", "route": "/dashboard/pwd", "icon": "🛣️", "summary": "Road damage, potholes, surface defects"},
        {"name": "Water", "route": "/dashboard/water", "icon": "💧", "summary": "Leakage, drainage and water supply faults"},
        {"name": "Sanitation", "route": "/dashboard/sanitation", "icon": "♻️", "summary": "Garbage, hygiene and waste dumping issues"},
        {"name": "Infrastructure", "route": "/dashboard/infrastructure", "icon": "🏗️", "summary": "Street lights, benches, poles and civic assets"},
    ]
    return render_template("admin_department_access.html", departments=departments)


@app.route("/dashboard/traffic")
@login_required
def traffic_dashboard():
    ensure_demo_session()
    return render_template("dashboard_traffic.html")


@app.route("/dashboard/pwd")
@login_required
def pwd_dashboard():
    ensure_demo_session()
    return render_template("dashboard_pwd.html")


@app.route("/dashboard/water")
@login_required
def water_dashboard():
    ensure_demo_session()
    return render_template("dashboard_water.html")


@app.route("/dashboard/sanitation")
@login_required
def sanitation_dashboard():
    ensure_demo_session()
    return render_template("dashboard_sanitation.html")


@app.route("/dashboard/infrastructure")
@login_required
def infrastructure_dashboard():
    ensure_demo_session()
    return render_template("dashboard_infrastructure.html")


@app.route("/api/complaints")
def get_complaints():
    zone, department, status = request.args.get("zone", "All"), request.args.get("dept", "All"), request.args.get("status", "All")
    limit = min(max(request.args.get("limit", 100, type=int), 1), 250)
    query, parameters = "SELECT * FROM complaints WHERE 1 = 1", []
    if zone != "All": query += " AND zone = ?"; parameters.append(zone)
    if department != "All": query += " AND category = ?"; parameters.append(department)
    if status != "All": query += " AND status = ?"; parameters.append(status)
    query += " ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, created_at DESC LIMIT ?"
    parameters.append(limit)
    with get_db() as db:
        rows = db.execute(query, parameters).fetchall()
    return jsonify([serialize_ticket(row) for row in rows])


@app.route("/api/complaints/track/<reference>")
def track_complaint(reference):
    normalized_reference = reference.strip().upper()
    with get_db() as db:
        row = db.execute("SELECT * FROM complaints WHERE reference = ?", (normalized_reference,)).fetchone()
    if row is None:
        return jsonify({"error": "No report was found for this reference."}), 404
    return jsonify(serialize_ticket(row))


@app.route("/api/analytics")
def get_analytics():
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        open_tickets = db.execute("SELECT COUNT(*) FROM complaints WHERE status NOT IN ('Resolved', 'Closed')").fetchone()[0]
        critical = db.execute("SELECT COUNT(*) FROM complaints WHERE severity IN ('Critical', 'High') AND status NOT IN ('Resolved', 'Closed')").fetchone()[0]
        resolved = db.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('Resolved', 'Closed')").fetchone()[0]
        avg_risk = db.execute("SELECT COALESCE(ROUND(AVG(risk_score)), 0) FROM complaints").fetchone()[0]
        zones = db.execute("SELECT zone, COUNT(*) AS count, SUM(CASE WHEN severity IN ('Critical', 'High') THEN 1 ELSE 0 END) AS urgent FROM complaints GROUP BY zone ORDER BY count DESC").fetchall()
    return jsonify({"total": total, "open": open_tickets, "critical": critical, "resolved": resolved, "resolution_rate": round((resolved / total) * 100) if total else 0, "average_risk": avg_risk, "zones": [dict(row) for row in zones], "generated_at": utcnow()})


@app.route("/api/predictions")
def get_predictions():
    zones = build_predictive_signals()
    lead = zones[0]
    return jsonify({
        "model": "Pulse Forecast v1 · explainable queue-density model",
        "headline": f"{lead['zone']} is {lead['level'].lower()} for the next 2 hours",
        "zones": zones,
        "generated_at": utcnow(),
    })


@app.route("/api/city-briefing")
def get_city_briefing():
    with get_db() as db:
        open_tickets = db.execute("SELECT COUNT(*) FROM complaints WHERE status NOT IN ('Resolved', 'Closed')").fetchone()[0]
        urgent = db.execute("SELECT COUNT(*) FROM complaints WHERE severity IN ('Critical', 'High') AND status NOT IN ('Resolved', 'Closed')").fetchone()[0]
        resolved = db.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('Resolved', 'Closed')").fetchone()[0]
        total = db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        hotspots = db.execute("""
            SELECT zone, category, COUNT(*) AS signals, ROUND(AVG(risk_score)) AS avg_risk,
                   SUM(CASE WHEN severity IN ('Critical', 'High') THEN 1 ELSE 0 END) AS urgent
            FROM complaints
            WHERE status NOT IN ('Resolved', 'Closed')
            GROUP BY zone, category
            ORDER BY urgent DESC, avg_risk DESC, signals DESC
            LIMIT 3
        """).fetchall()

    resolution_rate = round((resolved / total) * 100) if total else 100
    city_health = max(35, min(100, 100 - urgent * 11 - max(open_tickets - urgent, 0) * 3 + resolved * 2))
    hotspot_rows = [dict(row) for row in hotspots]
    if hotspot_rows:
        lead = hotspot_rows[0]
        headline = f"{lead['zone']} needs attention"
        narrative = (
            f"{lead['signals']} live {lead['category']} signal(s) are concentrated here, "
            f"with an average risk score of {lead['avg_risk']}/100."
        )
        action = f"Deploy {CATEGORY_CONFIG[lead['category']]['department']} to the priority cluster."
        forecast = "Escalation likely" if lead["urgent"] else "Monitor next 2 hours"
    else:
        headline = "City pulse is stable"
        narrative = "No active civic signals need a field dispatch right now. The network is ready for the next verified report."
        action = "Keep zone response teams on smart standby."
        forecast = "No hotspot forecast"
    return jsonify({
        "city_health": city_health,
        "response_integrity": resolution_rate,
        "active_signals": open_tickets,
        "priority_watchlist": urgent,
        "headline": headline,
        "narrative": narrative,
        "recommended_action": action,
        "forecast": forecast,
        "hotspots": hotspot_rows,
        "generated_at": utcnow(),
    })


@app.route("/api/submit", methods=["POST"])
def submit_report():
    if "image" not in request.files:
        return jsonify({"error": "Attach a photo before submitting the report."}), 400
    uploaded, category = request.files["image"], request.form.get("category", "PWD")
    if not uploaded.filename or not allowed_file(uploaded.filename):
        return jsonify({"error": "Use a JPG, PNG, or WEBP image under 12 MB."}), 400
    if category not in CATEGORY_CONFIG:
        return jsonify({"error": "Select a valid civic department."}), 400
    try:
        lat, lng = float(request.form.get("lat", "21.1458")), float(request.form.get("lng", "79.0882"))
    except (TypeError, ValueError):
        return jsonify({"error": "Location coordinates are invalid."}), 400
    if not (20.7 <= lat <= 21.7 and 78.5 <= lng <= 80.0):
        return jsonify({"error": "Please place the report pin within the Nagpur region."}), 400

    extension = secure_filename(uploaded.filename).rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4().hex}.{extension}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)
    uploaded.save(filepath)
    ai_result = analyze_civic_image(filepath, category)
    if ai_result["status"] == "Rejected":
        try: os.remove(filepath)
        except OSError: pass
        return jsonify(ai_result), 422

    zone, duplicate, config, severity = get_nagpur_zone(lat, lng), find_duplicate(lat, lng, category), CATEGORY_CONFIG[category], ai_result["severity"]
    sla_minutes = config["sla"][severity]
    status = "Priority Dispatch" if severity in {"Critical", "High"} else "Queued"
    created_at = utcnow()
    eta = (datetime.now(IST) + timedelta(minutes=sla_minutes)).strftime("%H:%M IST")
    reference = f"NP-{datetime.now(IST).strftime('%y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
    voice = request.form.get("voice_text", "").strip()[:600] or "No spoken description supplied"
    image_url = f"/static/uploads/{stored_filename}"
    with get_db() as db:
        cursor = db.execute("""INSERT INTO complaints (reference,lat,lng,category,department,zone,severity,risk_score,confidence,quality_score,detected_features,visual_signal,ai_summary,voice,status,sla_minutes,eta,image_url,duplicate_of,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (reference,lat,lng,category,config["department"],zone,severity,ai_result["risk_score"],ai_result["confidence"],ai_result["quality_score"],ai_result["features_detected"],ai_result["visual_signal"],ai_result["summary"],voice,status,sla_minutes,eta,image_url,duplicate["reference"] if duplicate else None,created_at,created_at))
        ticket_id = cursor.lastrowid
    ticket = {
        "id": ticket_id, "reference": reference, "status": status, "zone": zone,
        "category": category, "department": config["department"], "severity": severity,
        "risk_score": ai_result["risk_score"], "eta": eta, "sla_minutes": sla_minutes,
        "duplicate": duplicate,
    }
    whatsapp = send_whatsapp_notification(ticket)
    broadcast_ticket_event("ticket:created", ticket)
    karma_points = {"Critical": 80, "High": 60, "Medium": 35, "Low": 20}[severity]
    return jsonify({"message": "Report verified and routed to the municipal command queue.", "ticket": ticket, "whatsapp": whatsapp, "ai_analysis": ai_result, "gamification": {"karma_earned": karma_points, "badge": "Civic Sentinel" if karma_points >= 60 else "City Ally"}}), 201


@app.route("/api/complaints/<int:ticket_id>/status", methods=["PATCH"])
def update_complaint_status(ticket_id):
    status = (request.get_json(silent=True) or {}).get("status")
    valid_statuses = {"Queued", "Priority Dispatch", "Assigned", "In Progress", "Resolved", "Closed", "Rejected"}
    if status not in valid_statuses:
        return jsonify({"error": "Choose a valid ticket status."}), 400
    with get_db() as db:
        result = db.execute("UPDATE complaints SET status = ?, updated_at = ? WHERE id = ?", (status, utcnow(), ticket_id))
        if result.rowcount == 0:
            return jsonify({"error": "Ticket not found."}), 404
        row = db.execute("SELECT * FROM complaints WHERE id = ?", (ticket_id,)).fetchone()
    ticket = serialize_ticket(row)
    broadcast_ticket_event("ticket:updated", ticket)
    return jsonify(ticket)


@app.route("/api/complaints/<int:ticket_id>/reject", methods=["PATCH"])
def reject_complaint(ticket_id):
    payload = request.get_json(silent=True) or {}
    reason = (payload.get("reason") or "Rejected by civic operations.").strip()[:200]
    with get_db() as db:
        result = db.execute("UPDATE complaints SET status = ?, ai_summary = COALESCE(ai_summary, '') || ?, updated_at = ? WHERE id = ?", ("Rejected", f" | Rejected: {reason}", utcnow(), ticket_id))
        if result.rowcount == 0:
            return jsonify({"error": "Ticket not found."}), 404
        row = db.execute("SELECT * FROM complaints WHERE id = ?", (ticket_id,)).fetchone()
    ticket = serialize_ticket(row)
    broadcast_ticket_event("ticket:updated", ticket)
    return jsonify(ticket)


@app.route("/api/complaints/<int:ticket_id>", methods=["DELETE"])
def delete_complaint(ticket_id):
    with get_db() as db:
        result = db.execute("DELETE FROM complaints WHERE id = ?", (ticket_id,))
        if result.rowcount == 0:
            return jsonify({"error": "Ticket not found."}), 404
    return jsonify({"success": True, "deleted_id": ticket_id})


@app.route("/api/department-tickets")
def get_department_tickets():
    dept = request.args.get("dept", "Traffic").strip()

    dept_key = None
    for key, config in CATEGORY_CONFIG.items():
        if config["department"].lower() == dept.lower() or key.lower() == dept.lower():
            dept_key = key
            break

    if not dept_key:
        return jsonify({
            "error": "Invalid department",
            "valid_departments": list(CATEGORY_CONFIG.keys())
        }), 400

    dept_config = CATEGORY_CONFIG[dept_key]

    with get_db() as db:
        tickets = db.execute(
            """SELECT id, reference, category, zone, severity, status,
                      created_at, ai_summary, image_url
               FROM complaints
               WHERE department = ?
               ORDER BY
                   CASE WHEN severity='Critical' THEN 0
                        WHEN severity='High' THEN 1
                        WHEN severity='Medium' THEN 2
                        ELSE 3 END,
                   created_at DESC
               LIMIT 100
            """, (dept_config["department"],)
        ).fetchall()

        total = len(tickets)
        pending = sum(1 for t in tickets if t["status"] in {"Queued", "Priority Dispatch"})
        in_progress = sum(1 for t in tickets if t["status"] in {"Assigned", "In Progress"})
        completed = sum(1 for t in tickets if t["status"] in {"Resolved", "Closed"})

        critical = sum(1 for t in tickets if t["severity"] == "Critical")
        high = sum(1 for t in tickets if t["severity"] == "High")
        medium = sum(1 for t in tickets if t["severity"] == "Medium")
        low = sum(1 for t in tickets if t["severity"] == "Low")

        issue_types = {}
        for ticket in tickets:
            cat = ticket["category"]
            issue_types[cat] = issue_types.get(cat, 0) + 1

        zones = {}
        for ticket in tickets:
            zone = ticket["zone"]
            zones[zone] = zones.get(zone, 0) + 1

    dept_colors = {
        "Traffic": "#FF6B6B",
        "PWD": "#4ECDC4",
        "Sanitation": "#95E1D3",
        "Water": "#74B9FF",
        "Infrastructure": "#A29BFE"
    }

    dept_icons = {
        "Traffic": "🚦",
        "PWD": "🛣️",
        "Sanitation": "♻️",
        "Water": "💧",
        "Infrastructure": "🏗️"
    }

    return jsonify({
        "department": dept_key,
        "department_full": dept_config["department"],
        "icon": dept_icons.get(dept_key, "📋"),
        "color": dept_colors.get(dept_key, "#999"),
        "total": total,
        "pending": pending,
        "inProgress": in_progress,
        "completed": completed,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "tickets": [
            {
                "id": t["id"],
                "reference": t["reference"],
                "issue": t["ai_summary"][:50] + "..." if len(t["ai_summary"]) > 50 else t["ai_summary"],
                "zone": t["zone"],
                "severity": t["severity"],
                "status": t["status"],
                "created_at": t["created_at"],
                "image_url": t["image_url"]
            }
            for t in tickets
        ],
        "issueTypes": [
            {"type": issue, "count": count}
            for issue, count in sorted(issue_types.items(), key=lambda x: -x[1])
        ],
        "zones": [
            {"name": zone, "count": count}
            for zone, count in sorted(zones.items(), key=lambda x: -x[1])
        ],
        "sla": dept_config["sla"],
        "generated_at": utcnow()
    })


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(_error):
    return jsonify({"error": "Image is larger than 12 MB. Please use a smaller photo."}), 413


@app.errorhandler(500)
def handle_server_error(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "The server could not process this request. Please try again."}), 500
    return "Internal Server Error", 500


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Unexpected server error. Please try again."}), 500
    return "Internal Server Error", 500


init_db()

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)