from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash

from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = "dev-key-change-this-if-you-deploy"

STATUSES = ["Quoted", "Scheduled", "In Progress", "Done", "Invoiced"]


@app.route("/")
def dashboard():
    conn = get_connection()
    client_count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    open_jobs = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status != 'Done'"
    ).fetchone()[0]
    unpaid_total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE paid = 0"
    ).fetchone()[0]
    recent_jobs = conn.execute(
        """SELECT jobs.*, clients.name AS client_name
           FROM jobs JOIN clients ON jobs.client_id = clients.id
           ORDER BY jobs.id DESC LIMIT 6"""
    ).fetchall()
    conn.close()
    return render_template(
        "index.html",
        client_count=client_count,
        open_jobs=open_jobs,
        unpaid_total=unpaid_total,
        recent_jobs=recent_jobs,
    )


# ---------- Clients ----------

@app.route("/clients")
def clients():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return render_template("clients.html", clients=rows)


@app.route("/clients/add", methods=["GET", "POST"])
def add_client():
    if request.method == "POST":
        conn = get_connection()
        conn.execute(
            "INSERT INTO clients (name, phone, email, address, notes) VALUES (?, ?, ?, ?, ?)",
            (
                request.form["name"].strip(),
                request.form.get("phone", "").strip(),
                request.form.get("email", "").strip(),
                request.form.get("address", "").strip(),
                request.form.get("notes", "").strip(),
            ),
        )
        conn.commit()
        conn.close()
        flash("Client added.")
        return redirect(url_for("clients"))
    return render_template("client_form.html")


# ---------- Jobs ----------

@app.route("/jobs")
def jobs():
    conn = get_connection()
    rows = conn.execute(
        """SELECT jobs.*, clients.name AS client_name
           FROM jobs JOIN clients ON jobs.client_id = clients.id
           ORDER BY jobs.job_date DESC, jobs.id DESC"""
    ).fetchall()
    conn.close()
    return render_template("jobs.html", jobs=rows)


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    conn = get_connection()
    if request.method == "POST":
        conn.execute(
            """INSERT INTO jobs (client_id, title, description, status, job_date, address)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                request.form["client_id"],
                request.form["title"].strip(),
                request.form.get("description", "").strip(),
                request.form.get("status", "Quoted"),
                request.form.get("job_date") or date.today().isoformat(),
                request.form.get("address", "").strip(),
            ),
        )
        conn.commit()
        conn.close()
        flash("Job added.")
        return redirect(url_for("jobs"))
    client_list = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return render_template(
        "job_form.html", clients=client_list, statuses=STATUSES, today=date.today().isoformat()
    )


# ---------- Materials ----------

@app.route("/materials")
def materials():
    conn = get_connection()
    rows = conn.execute(
        """SELECT materials.*, jobs.title AS job_title
           FROM materials JOIN jobs ON materials.job_id = jobs.id
           ORDER BY materials.id DESC"""
    ).fetchall()
    conn.close()
    return render_template("materials.html", materials=rows)


@app.route("/materials/add", methods=["GET", "POST"])
def add_material():
    conn = get_connection()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO materials (job_id, name, quantity, unit_cost) VALUES (?, ?, ?, ?)",
            (
                request.form["job_id"],
                request.form["name"].strip(),
                float(request.form.get("quantity") or 1),
                float(request.form.get("unit_cost") or 0),
            ),
        )
        conn.commit()
        conn.close()
        flash("Material logged.")
        return redirect(url_for("materials"))
    job_list = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("material_form.html", jobs=job_list)


# ---------- Invoices ----------

@app.route("/invoices")
def invoices():
    conn = get_connection()
    rows = conn.execute(
        """SELECT invoices.*, jobs.title AS job_title, clients.name AS client_name
           FROM invoices
           JOIN jobs ON invoices.job_id = jobs.id
           JOIN clients ON jobs.client_id = clients.id
           ORDER BY invoices.issue_date DESC, invoices.id DESC"""
    ).fetchall()
    conn.close()
    return render_template("invoices.html", invoices=rows)


@app.route("/invoices/add", methods=["GET", "POST"])
def add_invoice():
    conn = get_connection()
    if request.method == "POST":
        conn.execute(
            """INSERT INTO invoices (job_id, amount, issue_date, due_date, paid)
               VALUES (?, ?, ?, ?, ?)""",
            (
                request.form["job_id"],
                float(request.form["amount"]),
                request.form.get("issue_date") or date.today().isoformat(),
                request.form.get("due_date") or "",
                1 if request.form.get("paid") == "on" else 0,
            ),
        )
        conn.commit()
        conn.close()
        flash("Invoice created.")
        return redirect(url_for("invoices"))
    job_list = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("invoice_form.html", jobs=job_list, today=date.today().isoformat())


@app.route("/invoices/<int:invoice_id>/toggle_paid", methods=["POST"])
def toggle_paid(invoice_id):
    conn = get_connection()
    conn.execute(
        "UPDATE invoices SET paid = 1 - paid WHERE id = ?", (invoice_id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("invoices"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
