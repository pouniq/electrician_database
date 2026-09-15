
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash

from database import get_connection, init_db


app = Flask(__name__)
app.secret_key = "dev-key-change-this-if-you-deploy"

STATUSES = ["Quoted", "Scheduled", "In Progress", "Done", "Invoiced"]


# ============================================================
# Dashboard
# ============================================================

@app.route("/")
def dashboard():
    conn = get_connection()

    customer_count = conn.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    open_jobs = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status != 'Done'"
    ).fetchone()[0]

    unpaid_total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE paid = 0"
    ).fetchone()[0]

    recent_jobs = conn.execute(
        """
        SELECT jobs.*, customers.name AS customer_name
        FROM jobs
        JOIN customers ON jobs.customer_id = customers.id
        ORDER BY jobs.id DESC
        LIMIT 6
        """
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        customer_count=customer_count,
        open_jobs=open_jobs,
        unpaid_total=unpaid_total,
        recent_jobs=recent_jobs,
    )


# ============================================================
# Customers
# ============================================================

@app.route("/customers")
def customers():
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM customers ORDER BY name"
    ).fetchall()

    conn.close()

    return render_template(
        "customers.html",
        customers=rows
    )


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        conn = get_connection()



        conn.execute(
        """
        INSERT INTO customers
        (name, last_name, phone, address, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            request.form["name"].strip(),
            request.form["last_name"].strip(),
            request.form.get("phone", "").strip(),
            request.form.get("address", "").strip(),
            request.form.get("notes", "").strip(),
        ),
    )
            
        
        conn.commit()
        conn.close()

        flash("Customer added.")

        return redirect(url_for("customers"))

    return render_template("customer_form.html")


# ============================================================
# Jobs
# ============================================================

@app.route("/jobs")
def jobs():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            jobs.*,
            customers.name AS customer_name,
            customers.last_name AS customer_last_name
        FROM jobs
        JOIN customers ON jobs.customer_id = customers.id
        ORDER BY jobs.job_date DESC, jobs.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template("jobs.html", jobs=rows);

@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    conn = get_connection()

    if request.method == "POST":
        conn.execute(
            """
            INSERT INTO jobs
            (customer_id, job_title, description, status, job_date, address, labor_pay)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["customer_id"],
                request.form["title"].strip(),
                request.form.get("description", "").strip(),
                request.form.get("status", "Quoted"),
                request.form.get("job_date") or date.today().isoformat(),
                request.form.get("address", "").strip(),
                request.form.get("labor_pay") or 0,
            ),
        )
        conn.commit()
        conn.close()
        flash("کار با موفقیت ثبت شد.")
        return redirect(url_for("jobs"))

    customer_list = conn.execute(
        "SELECT * FROM customers ORDER BY name, last_name"
    ).fetchall()
    conn.close()

    return render_template(
        "job_form.html",
        customers=customer_list,
        statuses=STATUSES,
        today=date.today().isoformat(),
    )

# ============================================================
# Materials
# ============================================================

@app.route("/materials")
def materials():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT materials.*, jobs.title AS job_title
        FROM materials
        JOIN jobs ON materials.job_id = jobs.id
        ORDER BY materials.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "materials.html",
        materials=rows
    )


@app.route("/materials/add", methods=["GET", "POST"])
def add_material():
    conn = get_connection()

    if request.method == "POST":
        conn.execute(
            """
            INSERT INTO materials
            (job_id, name, quantity, unit_cost)
            VALUES (?, ?, ?, ?)
            """,
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

    job_list = conn.execute(
        "SELECT * FROM jobs ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "material_form.html",
        jobs=job_list
    )


# ============================================================
# Payments
# ============================================================

@app.route("/payments")
def payments():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            payments.*,
            jobs.title AS job_title,
            customers.name AS customer_name
        FROM payments
        JOIN jobs
            ON payments.job_id = jobs.id
        JOIN customers
            ON jobs.customer_id = customers.id
        ORDER BY payments.issue_date DESC, payments.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "payments.html",
        payments=rows
    )


@app.route("/payments/add", methods=["GET", "POST"])
def add_payment():
    conn = get_connection()

    if request.method == "POST":
        conn.execute(
            """
            INSERT INTO payments
            (job_id, amount, issue_date, due_date, paid)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.form["job_id"],
                float(request.form["amount"]),
                request.form.get("issue_date")
                or date.today().isoformat(),
                request.form.get("due_date") or "",
                1 if request.form.get("paid") == "on" else 0,
            ),
        )

        conn.commit()
        conn.close()

        flash("Payment created.")

        return redirect(url_for("payments"))

    job_list = conn.execute(
        "SELECT * FROM jobs ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "payment_form.html",
        jobs=job_list,
        today=date.today().isoformat(),
    )


@app.route("/payments/<int:payment_id>/toggle_paid", methods=["POST"])
def toggle_paid(payment_id):
    conn = get_connection()

    conn.execute(
        """
        UPDATE payments
        SET paid = 1 - paid
        WHERE id = ?
        """,
        (payment_id,),
    )

    conn.commit()
    conn.close()

    return redirect(url_for("payments"))


# ============================================================
# Run application
# ============================================================

if __name__ == "__main__":
    init_db()
    app.run(
        debug=True,
        port=5051
    )

