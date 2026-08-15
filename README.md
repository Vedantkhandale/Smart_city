🚦 Nagpur Pulse: AI-Driven Smart City Command Center

Nagpur Pulse is a next-generation **PWA (Progressive Web App)** designed to revolutionize civic grievance reporting in Nagpur. By leveraging **OpenCV for AI-based image analysis** and **real-time WhatsApp API routing**, the platform bridges the gap between citizens and municipal authorities.

🚀 Key Features

*   **Neural AI Scanner:** Uses OpenCV to analyze real-time camera frames, detecting traffic jams, potholes, and garbage dumps with severity-based bounding box feedback.
*   **Voice AI Integration:** Multi-lingual (Hindi/Marathi/English) voice-to-text parser for hands-free complaint filing.
*   **Real-Time Geofencing:** Automatically routes grievances to the correct municipal zone (e.g., Dharampeth, Dhantoli) based on live GPS coordinates.
*   **Predictive Analytics:** AI-driven hazard probability engine that forecasts traffic hotspots.
*   **Civic Karma (Gamification):** Built-in XP system to reward active citizens, fostering community engagement.
*   **Automated Emergency Routing:** Immediate dispatch of high-severity alerts via Meta WhatsApp Cloud API directly to department heads.

🛠️ Tech Stack

*   **Frontend:** HTML5, TailwindCSS, JavaScript, Leaflet.js (for Map Heatmaps).
*   **Backend:** Flask (Python).
*   **AI/Vision:** OpenCV (Image Processing, Contour Analysis, Blur Detection).
*   **Real-time:** WebSockets (via Flask-SocketIO) for live ticket updates.
*   **Integrations:** Meta Cloud WhatsApp API, OpenStreetMap API.

 📂 Project Structure

text
nagpur-pulse/
├── app.py                # Flask Backend & AI Logic
├── static/
│   ├── uploads/          # AI Processed Images
│   └── css/              # Custom Styles
├── templates/
│   ├── index.html        # Citizen AI Portal
│   └── admin_dashboard.html # Command Center
└── requirements.txt      # Dependencies
