from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "attendance.db"


def get_db():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    return con


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM teachers WHERE email=? AND password=?",
            (email, password)
        )
        teacher = cur.fetchone()
        con.close()

        if teacher:
            session["teacher_id"] = teacher["id"]
            session["teacher_email"] = teacher["email"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid Email or Password"

    return render_template("login.html", error=error)


@app.route("/teacher-register", methods=["POST"])
def teacher_register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    con = get_db()
    cur = con.cursor()

    try:
        cur.execute(
            "INSERT INTO teachers (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        con.commit()
        flash("Teacher registered successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Email already registered!", "danger")
    finally:
        con.close()

    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", email=session["teacher_email"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/add-student", methods=["GET", "POST"])
def add_student():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        name = request.form["name"]
        department = request.form["department"]
        teacher_id = session["teacher_id"]

        con = get_db()
        cur = con.cursor()

        try:
            cur.execute("""
                INSERT INTO students (roll_no, name, department, teacher_id)
                VALUES (?, ?, ?, ?)
            """, (roll_no, name, department, teacher_id))
            con.commit()
            flash("Student added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Roll No already exists!", "danger")
        finally:
            con.close()

        return redirect(url_for("add_student"))

    return render_template("add_student.html")


@app.route("/view-students")
def view_students():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM students WHERE teacher_id=?",
        (session["teacher_id"],)
    )
    students = cur.fetchall()
    con.close()

    return render_template("view_students.html", students=students)


@app.route("/update-student/<int:id>", methods=["GET", "POST"])
def update_student(id):
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        name = request.form["name"]
        department = request.form["department"]

        cur.execute("""
            UPDATE students
            SET roll_no=?, name=?, department=?
            WHERE id=? AND teacher_id=?
        """, (roll_no, name, department, id, session["teacher_id"]))

        con.commit()
        con.close()

        flash("Student updated successfully!", "success")
        return redirect(url_for("view_students"))

    cur.execute(
        "SELECT * FROM students WHERE id=? AND teacher_id=?",
        (id, session["teacher_id"])
    )
    student = cur.fetchone()
    con.close()

    if not student:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("view_students"))

    return render_template("update_student.html", student=student)


@app.route("/delete-student/<int:id>")
def delete_student(id):
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute(
        "DELETE FROM students WHERE id=? AND teacher_id=?",
        (id, session["teacher_id"])
    )
    con.commit()
    con.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for("view_students"))


@app.route("/mark-attendance", methods=["GET", "POST"])
def mark_attendance():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM students WHERE teacher_id=?",
        (session["teacher_id"],)
    )
    students = cur.fetchall()

    if request.method == "POST":
        attendance_date = request.form["date"]

        for student in students:
            status = request.form.get(f"status_{student['id']}", "Absent")
            cur.execute("""
                INSERT INTO attendance (student_id, date, status)
                VALUES (?, ?, ?)
            """, (student["id"], attendance_date, status))

        con.commit()
        con.close()
        flash("Attendance marked successfully!", "success")
        return redirect(url_for("mark_attendance"))

    con.close()
    return render_template(
        "mark_attendance.html",
        students=students,
        today=date.today().strftime("%Y-%m-%d")
    )


@app.route("/report")
def report():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        SELECT s.roll_no, s.name, s.department, a.date, a.status
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        WHERE s.teacher_id = ?
        ORDER BY a.date DESC
    """, (session["teacher_id"],))

    records = cur.fetchall()
    con.close()

    return render_template("report.html", records=records)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 9545))
    app.run(debug=True, host="0.0.0.0", port=port)
