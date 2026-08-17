# Nagpur Pulse — running it locally with a real database

```
cd backend
pip install -r requirements.txt
python3 app.py
```

Then open **http://localhost:5000** — the backend serves the whole frontend
(`index.html`, `login.html`, `signup.html`, `admin.html`, `assets/`) and
backs sign-up / sign-in with a real SQLite database.

On first run it creates `backend/nagpur_pulse.db` with two tables:

- `users` — username, optional email, a **hashed** password (never stored in
  plain text), created_at
- `tickets` — every submitted civic report, so `/login` → sign up → submit a
  report → track it by reference all work end-to-end against real data

## Pages
| Page | Purpose |
|---|---|
| `/` (index.html) | Citizen report flow — camera/upload, voice note, map pin, submit |
| `/login.html` | Command Center sign-in (real DB check; falls back to the demo login `admin` / `pulse2026` only if the backend isn't running) |
| `/signup.html` | Create a new Command Center account |
| `/admin.html` | Lands here after a successful sign-in / sign-up |

## Notes
- Delete `backend/nagpur_pulse.db` any time to start with a clean database.
- This is a local dev server (`debug=True`) — don't deploy it as-is to the
  internet; swap in a production WSGI server and turn debug off first.