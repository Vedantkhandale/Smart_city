# 🏢 Department Dashboard Guide

## Quick Start

### Access Department Dashboards
Each department can access their dedicated dashboard with work queues:

1. **Traffic Police** 
   - URL: `/department_dashboard.html?dept=Traffic`
   - Issues: Traffic congestion, signal faults, road obstructions
   - Status: 🚦 Live

2. **PWD Roads**
   - URL: `/department_dashboard.html?dept=PWD`
   - Issues: Potholes, road damage, pavements
   - Status: 🛣️ Live

3. **Sanitation**
   - URL: `/department_dashboard.html?dept=Sanitation`
   - Issues: Garbage, waste accumulation, drainage
   - Status: ♻️ Live

4. **Water Works**
   - URL: `/department_dashboard.html?dept=Water`
   - Issues: Water leaks, flooding, pipe damage
   - Status: 💧 Live

5. **Infrastructure (NEW!)**
   - URL: `/department_dashboard.html?dept=Infrastructure`
   - Issues: Broken street lights, poles, benches, fallen trees
   - Status: 🏗️ Live

---

## 🚀 API Endpoints

### Get Department Tickets
```
GET /api/department-tickets?dept=Traffic|PWD|Sanitation|Water|Infrastructure
```

**Response Format:**
```json
{
  "department": "Traffic",
  "department_full": "Traffic Police",
  "icon": "🚦",
  "color": "#FF6B6B",
  "total": 42,
  "pending": 15,
  "inProgress": 8,
  "completed": 19,
  "critical": 3,
  "high": 7,
  "medium": 15,
  "low": 17,
  "tickets": [
    {
      "id": 1,
      "reference": "NP-250115-ABCDE",
      "issue": "Traffic signal non-functional at Plaza...",
      "zone": "Dharampeth Zone-1",
      "severity": "Critical",
      "status": "Assigned",
      "created_at": "2025-01-15T10:30:00Z",
      "image_url": "/static/uploads/img_001.jpg"
    }
  ],
  "issueTypes": [
    {"type": "Traffic", "count": 12},
    {"type": "Obstruction", "count": 8}
  ],
  "zones": [
    {"name": "Dharampeth Zone-1", "count": 25},
    {"name": "Dhantoli Zone-2", "count": 10}
  ],
  "sla": {"Critical": 20, "High": 45, "Medium": 120, "Low": 360},
  "generated_at": "2025-01-15T15:30:00Z"
}
```

---

## 📊 Dashboard Features

### Stats Cards (Animated)
- **Total Assigned**: All tickets in department queue
- **Pending Action**: Queued + Priority Dispatch status
- **In Progress**: Assigned or In Progress status
- **Completed**: Resolved or Closed status

### Filter Tabs
- **All**: Show all tickets
- **Pending**: Queued, Priority Dispatch
- **In Progress**: Assigned, In Progress
- **Completed**: Resolved, Closed

### Severity Badges
- 🔴 **Critical**: Respond in 20-45 minutes (Traffic/Infrastructure)
- 🟠 **High**: Respond in 45-90 minutes
- 🔵 **Medium**: Respond in 120-240 minutes  
- 🟢 **Low**: Respond in 360+ minutes

### Sidebar Analytics
- **Priority Breakdown**: Count by severity level
- **Issue Types**: Count by category
- **Zone Coverage**: Geographic distribution

---

## 🤖 AI Analysis Features

### Smart Street Light Detection
When citizens report an issue under "Infrastructure":
1. Image is captured and analyzed for:
   - **Dark patches** (unlit fixtures)
   - **Linear damage** (broken poles)
   - **Missing fixtures** (stolen/fallen)

2. AI confidence is boosted when specific features detected
3. Risk score adjusted based on visibility patterns
4. **Municipality** department auto-receives for routing to proper sub-department

### Enhanced Issue Classification
Each category now detects:

**Traffic Category:**
- Signal faults
- Road obstructions
- Parking violations

**PWD Category:**
- Potholes
- Road cracks
- Manhole cover issues

**Sanitation Category:**
- Garbage piles
- Illegal dumping
- Drain blockages

**Water Category:**
- Water leaks
- Flooding
- Stagnant water

**Infrastructure Category (NEW):**
- Broken street lights ✨
- Damaged poles
- Missing fixtures
- Fallen trees

---

## 📱 How Citizens Report Street Lights

### Reporting Flow
1. **Open Nagpur Pulse** → Click "Capture the civic issue"
2. **Take Photo** → Frame the broken street light clearly
3. **Select Category** → Choose "🏗️ Street light broken / infrastructure damage"
4. **Voice Note** (Optional) → "Street light is not working"
5. **Confirm Location** → Pin the exact spot on map
6. **Submit** → AI analyzes and routes to Infrastructure department

### AI Processing
- Detects dark circular patches (unlit fixtures)
- Analyzes edge patterns (broken glass, damaged fixtures)
- Scores confidence based on feature detection
- **Routes to**: Municipal Corporation → Infrastructure → Street Lighting Sub-dept

---

## 🎯 SLA Response Times

**Infrastructure Department:**
- 🔴 Critical: **25 minutes**
- 🟠 High: **60 minutes**
- 🔵 Medium: **180 minutes**
- 🟢 Low: **360 minutes**

---

## 💾 Database Schema

All tickets stored in SQLite `complaints` table:

```sql
CREATE TABLE complaints (
  id INTEGER PRIMARY KEY,
  reference TEXT UNIQUE,        -- NP-YYMMDD-XXXXX
  lat REAL, lng REAL,           -- GPS coordinates
  category TEXT,                 -- Traffic/PWD/Sanitation/Water/Infrastructure
  department TEXT,               -- Department name
  zone TEXT,                     -- Nagpur zone
  severity TEXT,                 -- Critical/High/Medium/Low
  risk_score INTEGER,            -- 18-98
  confidence INTEGER,            -- 62-96%
  quality_score INTEGER,         -- 25-99%
  detected_features INTEGER,     -- Count of visual regions
  visual_signal TEXT,            -- What the AI detected
  ai_summary TEXT,               -- Long description
  voice TEXT,                    -- Citizen's voice note
  status TEXT,                   -- Queued/Assigned/In Progress/Resolved
  sla_minutes INTEGER,           -- Response target
  eta TEXT,                      -- Human-readable ETA
  image_url TEXT,                -- Path to uploaded image
  duplicate_of TEXT,             -- Reference if duplicate
  created_at TEXT,               -- Timestamp
  updated_at TEXT                -- Last modified
)
```

---

## 🔗 Integration Links

- **Public Portal**: [http://localhost:5000/](http://localhost:5000/)
- **Command Center**: [http://localhost:5000/admin](http://localhost:5000/admin)
- **Department Dashboards**: 
  - Traffic: [?dept=Traffic](http://localhost:5000/templates/department_dashboard.html?dept=Traffic)
  - PWD: [?dept=PWD](http://localhost:5000/templates/department_dashboard.html?dept=PWD)
  - Sanitation: [?dept=Sanitation](http://localhost:5000/templates/department_dashboard.html?dept=Sanitation)
  - Water: [?dept=Water](http://localhost:5000/templates/department_dashboard.html?dept=Water)
  - Infrastructure: [?dept=Infrastructure](http://localhost:5000/templates/department_dashboard.html?dept=Infrastructure)

---

## 📋 Testing the System

### Test Case 1: Report a Broken Street Light
1. Go to citizen portal
2. Take/upload photo of broken street light
3. Select "🏗️ Street light broken / infrastructure damage"
4. Add voice: "This light on Main Road is not working"
5. Confirm GPS location
6. Submit

**Expected Result:**
- ✅ Ticket created with `category=Infrastructure`
- ✅ Auto-routed to Municipal Corporation
- ✅ Appears in Infrastructure department dashboard
- ✅ Risk score boosted if dark fixtures detected

### Test Case 2: Check Department Dashboard
1. Go to Infrastructure dashboard: `?dept=Infrastructure`
2. Should see:
   - 🏗️ Department badge
   - Stats for all tickets
   - List of street light reports
   - Filter options working
   - Auto-refresh every 30 seconds

---

## 🚨 Troubleshooting

**Dashboard not showing tickets?**
- Check if API endpoint is responding: `curl http://localhost:5000/api/department-tickets?dept=Traffic`
- Verify department name matches exactly
- Check database has tickets with that department

**Street light detection not working?**
- Ensure image shows clear dark patches (unlit fixtures)
- Image quality score must be >40 for acceptance
- Try photos taken in evening/night (better contrast)

**Wrong department assigned?**
- Verify category was selected correctly
- Check AI summary in ticket details
- May need clearer photo with focused issue

---

## 📞 Support

For issues or questions:
- Check dashboard logs in browser console
- Review AI analysis in ticket details (risk score breakdown)
- Verify network connectivity to `/api/` endpoints

**Last Updated:** January 2025  
**Version:** 2.0 - Department Routing System  
**Status:** 🟢 PRODUCTION READY
