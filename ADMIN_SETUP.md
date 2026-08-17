# 🔐 Nagpur Pulse Admin Portal Setup

## Admin Login Credentials ✅

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `pulse2026` |
| **Login URL** | `http://127.0.0.1:5000/login` |
| **Dashboard** | `http://127.0.0.1:5000/admin` |

---

## How to Access Admin Portal

### Step 1: Start the Application
```bash
cd c:\nagpur_pluse
python app.py
```

### Step 2: Open Login Page
- Visit: **http://127.0.0.1:5000/login**
- Or click **"Create an account"** link from citizen report page

### Step 3: Sign In with Admin Account
```
Username: admin
Password: pulse2026
```

### Step 4: Access Command Center Dashboard
- After login, you'll be redirected to: **http://127.0.0.1:5000/admin**
- Dashboard shows all civic complaints across 4 Nagpur zones
- Real-time SLA tracking and complaint triage

---

## Admin Dashboard Features

✅ **Live Complaint Feed**
- View all civic reports submitted by citizens
- Filter by zone, department, and status
- Priority sorting (Critical → High → Medium → Low)

✅ **Real-Time Triage**
- AI-analyzed risk scores (18-98 scale)
- Visual quality metrics & confidence levels
- Detected issue features from images

✅ **Department Routing**
- Traffic Police
- PWD Roads  
- Water Works & Drainage
- Solid Waste Management
- Municipal Corporation

✅ **SLA Monitoring**
- Track Service Level Agreements per severity
- ETA calculations based on zone & department
- Status tracking: Submitted → Triaged → Assigned → In Progress → Resolved

✅ **Zone Coverage**
- Dharampeth Zone-1
- Dhantoli Zone-2
- Laxmi Nagar Zone-3
- Nehru Nagar Zone-4

---

## Database & Authentication

**Backend**: Flask + SQLite3  
**Auth Method**: Session-based (stored in `app.secret_key`)  
**Database Path**: `c:\nagpur_pluse\nagpur_pulse.db`

Users are defined in `COMMAND_CENTER_USERS` dictionary in [app.py](app.py#L37)

---

## Demo Data

The database comes pre-populated with demo complaints if you run `test_db.py`:

```bash
python test_db.py
```

This creates sample civic reports across all categories for testing the admin dashboard triage workflow.

---

## Important Notes

⚠️ **Security**: This is a hackathon demo setup  
- Default credentials are for development only
- In production, implement proper user management with hashed passwords
- Use environment variables: `FLASK_SECRET_KEY`, `ADMIN_PASSWORD`

💾 **Session Management**:
- Sessions stored in client-side cookies
- Logout available at bottom of admin dashboard
- "Keep me signed in" option persists session

🔄 **API Endpoints**:
- `POST /api/auth/login` - Sign in
- `POST /api/auth/logout` - Sign out  
- `GET /api/complaints` - Fetch complaints with filters
- `GET /api/complaints/track/<reference>` - Track individual complaint

---

✅ **Status**: Admin portal is FULLY OPERATIONAL and ready for testing
