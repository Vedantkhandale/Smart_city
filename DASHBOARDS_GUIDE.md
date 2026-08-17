# 🎯 Admin & Department Dashboards - Complete Setup Guide

## What's New

✅ **Admin Dashboard** - View ALL complaints from all 5 departments in one place  
✅ **5 Department Dashboards** - Each department has their own filtered view  
✅ **Real-Time Images** - Every complaint shows the uploaded photo  
✅ **Live Filtering** - Filter by zone, status, severity  
✅ **Auto-Refresh** - Updates every 5 seconds  
✅ **Statistics** - Live counts (Total, Critical, Pending, Resolved)

---

## 📊 Dashboard URLs

### Admin Dashboard (See Everything)
```
http://127.0.0.1:5000/admin
```

### Department Dashboards
```
http://127.0.0.1:5000/dashboard/traffic        🚗 Traffic Police
http://127.0.0.1:5000/dashboard/pwd            🛣️ PWD Roads
http://127.0.0.1:5000/dashboard/water          💧 Water Works & Drainage
http://127.0.0.1:5000/dashboard/sanitation     🧹 Sanitation & Waste
http://127.0.0.1:5000/dashboard/infrastructure 🏗️ Infrastructure & Municipal
```

---

## 🔐 Login Credentials

All dashboards require login with:
```
Username: admin
Password: pulse2026
Login Page: http://127.0.0.1:5000/login
```

---

## 🎨 Admin Dashboard Features

### Real-Time Statistics
- **Total Reports** - All complaints count
- **Critical** - Critical severity incidents
- **High Priority** - High severity incidents  
- **Resolved** - Completed cases

### Filtering Options
1. **Department Filter** (Quick buttons with emojis)
   - All Departments
   - Traffic Police
   - PWD Roads
   - Water Works
   - Sanitation
   - Infrastructure

2. **Zone Filter**
   - Dharampeth Zone-1
   - Dhantoli Zone-2
   - Laxmi Nagar Zone-3
   - Nehru Nagar Zone-4

3. **Status Filter**
   - All Status
   - Priority Dispatch
   - Queued
   - Assigned
   - In Progress
   - Resolved

### Card View
Each complaint shows:
- 📸 Full image/photo
- 📌 Reference number (NP-YYMMDD-XXXXX)
- 🔴 Severity badge (Critical/High/Medium/Low)
- 📍 Zone location
- ⏱️ Current status
- ⚠️ Risk score (0-100)
- ⏰ ETA to response

---

## 🏢 Department Dashboard Features

Each department staff can access their filtered view showing:
- ✅ Only their department's complaints
- ✅ Images of reported issues
- ✅ Zone and status filters
- ✅ Live statistics for their department
- ✅ Risk scores and response times
- ✅ Quick navigation back to admin

### Department Specific Features

**Traffic Police Dashboard**
- Signal faults, traffic jams, parking violations, accidents
- Focus on road congestion and safety

**PWD Roads Dashboard**
- Potholes, road cracks, shoulder erosion, surface damage
- Infrastructure maintenance focus

**Water Works Dashboard**
- Water leaks, flooding, drainage obstruction, stagnant water
- Utility failure detection

**Sanitation Dashboard**
- Garbage piles, illegal dumping, street cleaning, waste
- Health and hygiene focus

**Infrastructure Dashboard**
- Street lights, benches, trees, poles, signs
- Public asset maintenance

---

## 🔄 How It Works

1. **Citizen submits complaint** (index.html)
   - Takes photo with camera
   - Records voice note
   - Selects category (Traffic, PWD, Water, etc.)
   - Submits location and description

2. **AI analyzes image**
   - Calculates risk score (18-98)
   - Detects issue features
   - Assigns severity level
   - Routes to department

3. **Admin reviews** (admin_dashboard.html)
   - Sees ALL incoming reports
   - Can filter by any criteria
   - Monitors SLA compliance
   - Assigns tickets

4. **Department staff acts** (department dashboard)
   - Reviews their queue
   - Updates status
   - Tracks progress
   - Completes work

---

## 💾 Database Integration

All dashboards query from the same SQLite database:
- Table: `complaints`
- Columns: reference, lat, lng, category, department, zone, severity, risk_score, status, image_url, voice, eta, created_at, etc.

API Endpoint Used:
```
GET /api/complaints?limit=250
    &zone=<zone>        (optional)
    &dept=<category>    (optional)
    &status=<status>    (optional)
```

---

## 🛡️ Security

✅ Session-based authentication  
✅ Login required on all dashboards  
✅ Admin credentials stored in app.py  
✅ Server-side filtering validation  
✅ Image URLs routed through Flask

---

## 📈 Performance

- **Auto-refresh**: 5 second interval
- **Limit**: 250 complaints per query (configurable)
- **Responsive Design**: Works on mobile, tablet, desktop
- **Image Optimization**: Lazy-loaded from /static/uploads/
- **Real-time Stats**: Calculated client-side

---

## 🚀 Next Steps

### To Add More Users:
Edit `app.py` line ~37:
```python
COMMAND_CENTER_USERS = {
    "admin": {"password": "pulse2026", "display_name": "Admin"},
    "traffic_lead": {"password": "traffic123", "display_name": "Traffic Lead"},
    "pwd_chief": {"password": "pwd456", "display_name": "PWD Chief"},
    # Add more...
}
```

### To Customize Admin Filters:
- Edit `admin_dashboard.html` line ~100-150
- Add/remove department buttons
- Modify zone list
- Change status options

### To Add Department-Specific Logic:
- Each dashboard loads via `/api/complaints?dept=X`
- Can be extended with department branding
- Add department-specific workflows
- Integrate with existing systems

---

## 🎯 Admin Access Path

1. **Go to**: http://127.0.0.1:5000/login
2. **Enter**: 
   - Username: `admin`
   - Password: `pulse2026`
3. **Click**: "Sign in to console"
4. **See**: Admin dashboard with ALL reports
5. **Filter**: By department, zone, status, severity
6. **View**: Full images and complaint details

---

## ✅ Testing Checklist

- [x] Admin dashboard loads all departments
- [x] Department filters work
- [x] Images display correctly
- [x] Real-time refresh working
- [x] Statistics update live
- [x] Zone filters working
- [x] Status filters working
- [x] Severity badges showing
- [x] Risk scores visible
- [x] ETA times correct
- [x] Department dashboards load
- [x] Back to Admin links work
- [x] Session protection active
- [x] Responsive on mobile
- [x] App doesn't crash

---

**Status**: ✅ COMPLETE - All dashboards ready for production use
