CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL UNIQUE,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    category TEXT NOT NULL,
    department TEXT NOT NULL,
    zone TEXT NOT NULL,
    severity TEXT NOT NULL,
    risk_score INTEGER NOT NULL,
    confidence INTEGER NOT NULL,
    quality_score INTEGER NOT NULL,
    detected_features INTEGER NOT NULL,
    visual_signal TEXT NOT NULL,
    ai_summary TEXT NOT NULL,
    voice TEXT NOT NULL,
    status TEXT NOT NULL,
    sla_minutes INTEGER NOT NULL,
    eta TEXT NOT NULL,
    image_url TEXT NOT NULL,
    duplicate_of TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

INSERT OR IGNORE INTO complaints (
    reference, lat, lng, category, department, zone, severity, risk_score,
    confidence, quality_score, detected_features, visual_signal, ai_summary,
    voice, status, sla_minutes, eta, image_url, duplicate_of, created_at, updated_at
) VALUES (
    'NP-260817-AB12C', 21.1458, 79.0882, 'Traffic', 'Traffic Police', 'Dharampeth Zone-1', 'High', 72,
    90, 88, 4, 'road occupancy / signal obstruction',
    'Severe traffic congestion near signal with queue buildup and restricted movement.',
    'Heavy traffic near the signal', 'Priority Dispatch', 45, '18:45 IST',
    '/static/uploads/demo_traffic.jpg', NULL,
    '2026-08-17T12:00:00+05:30', '2026-08-17T12:00:00+05:30'
);

INSERT OR IGNORE INTO complaints (
    reference, lat, lng, category, department, zone, severity, risk_score,
    confidence, quality_score, detected_features, visual_signal, ai_summary,
    voice, status, sla_minutes, eta, image_url, duplicate_of, created_at, updated_at
) VALUES (
    'NP-260817-CD34F', 21.1325, 79.1011, 'PWD', 'PWD Roads', 'Dhantoli Zone-2', 'Medium', 56,
    84, 80, 3, 'surface discontinuity / road damage',
    'Pothole and broken road surface detected, creating risk for small vehicles and pedestrians.',
    'Road is broken near the lane', 'Queued', 120, '22:00 IST',
    '/static/uploads/demo_pwd.jpg', NULL,
    '2026-08-17T13:15:00+05:30', '2026-08-17T13:15:00+05:30'
);

INSERT OR IGNORE INTO complaints (
    reference, lat, lng, category, department, zone, severity, risk_score,
    confidence, quality_score, detected_features, visual_signal, ai_summary,
    voice, status, sla_minutes, eta, image_url, duplicate_of, created_at, updated_at
) VALUES (
    'NP-260817-EF56H', 21.1201, 79.0632, 'Sanitation', 'Solid Waste Management', 'Laxmi Nagar Zone-3', 'Critical', 81,
    94, 92, 5, 'waste accumulation / hygiene risk',
    'Garbage pile and blocked drain creating hygiene risk and potential public nuisance.',
    'Garbage is piled outside the market', 'Priority Dispatch', 60, '17:45 IST',
    '/static/uploads/demo_sanitation.jpg', NULL,
    '2026-08-17T14:35:00+05:30', '2026-08-17T14:35:00+05:30'
);

INSERT OR IGNORE INTO complaints (
    reference, lat, lng, category, department, zone, severity, risk_score,
    confidence, quality_score, detected_features, visual_signal, ai_summary,
    voice, status, sla_minutes, eta, image_url, duplicate_of, created_at, updated_at
) VALUES (
    'NP-260817-GH78J', 21.1098, 79.0748, 'Water', 'Water Works & Drainage', 'Nehru Nagar Zone-4', 'Low', 32,
    76, 70, 2, 'water leak / drainage obstruction',
    'Minor water leakage observed with localized drainage concern near residential lane.',
    'Water is leaking slowly', 'Queued', 240, '20:00 IST',
    '/static/uploads/demo_water.jpg', NULL,
    '2026-08-17T15:50:00+05:30', '2026-08-17T15:50:00+05:30'
);
