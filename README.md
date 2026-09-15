# Site Log — personal electrician tracker

A small local web app for tracking clients, jobs, materials, and invoices.
Runs on your machine, stores everything in a single SQLite file.

## Setup

```bash
cd electrician-db
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5050** in your browser.

The database file `electrician.db` is created automatically on first run,
in the same folder as `app.py`.

## What it tracks

- **Clients** — name, phone, email, address, notes (panel type, gate code, etc.)
- **Jobs** — linked to a client, with status (Quoted / Scheduled / In Progress / Done / Invoiced), date, site address
- **Materials** — linked to a job, with quantity and unit cost
- **Invoices** — linked to a job, with amount, issue/due dates, and a paid/unpaid toggle

The dashboard shows client count, open jobs, and total outstanding invoice amount.

## Structure

```
electrician-db/
  app.py           Flask routes
  database.py      SQLite schema + connection helper
  templates/        HTML pages (Jinja2)
  static/style.css  Styling
  requirements.txt
```

## Extending it

- **Edit/delete**: currently insert + list only, plus a paid/unpaid toggle on
  invoices. Add `UPDATE`/`DELETE` routes in `app.py` following the same
  pattern as the existing `toggle_paid` route if you want full editing.
- **Backups**: `electrician.db` is a single file — copy it anywhere to back up
  or move your data (e.g. onto your external drive).
- **Hosting it**: this is built to run locally. To put it on a home server or
  small VPS, swap `app.run(debug=True, ...)` for a production server (e.g.
  `gunicorn app:app`), and turn `debug` off.
- **Switching databases**: if you outgrow SQLite, `database.py` is the only
  file that needs to change — the rest of the app talks to it through
  `get_connection()`.
