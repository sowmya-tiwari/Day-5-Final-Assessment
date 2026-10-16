
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "day5assessment_secret_key"

DATABASE = "students.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            course TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


create_table()


# Level 1 and Level 2: Registration
@app.route("/")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        age = request.form.get("age", "")
        gender = request.form.get("gender", "")
        course = request.form.get("course", "")
        password = request.form.get("password", "")

        if not all([name, email, age, gender, course, password]):
            return "All fields are required!", 400

        if not age.isdigit():
            return "Age must be a number!", 400

        if len(password) < 6:
            return "Password must contain at least 6 characters!", 400

        conn = get_db()

        try:
            cursor = conn.execute("""
                INSERT INTO students
                (name, email, age, gender, course, password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name, email, int(age), gender, course,
                generate_password_hash(password)
            ))
            conn.commit()
            student_id = cursor.lastrowid
            return redirect(url_for("success", student_id=student_id))

        except sqlite3.IntegrityError:
            return "This email is already registered!", 400

        except sqlite3.Error:
            return "Database error. Please try again.", 500

        finally:
            conn.close()

    return render_template("register.html")


# Level 2: Success page
@app.route("/success/<int:student_id>")
def success(student_id):
    conn = get_db()
    student = conn.execute(
        "SELECT name FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    conn.close()

    if student is None:
        return redirect(url_for("register"))

    return render_template("success.html", name=student["name"])


# Level 3: Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        student = conn.execute(
            "SELECT * FROM students WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if student and check_password_hash(student["password"], password):
            session["student_id"] = student["id"]
            return redirect(url_for("profile"))

        error = "Invalid email or password!"

    return render_template("login.html", error=error)


# Level 3 and Level 4: Profile dashboard
@app.route("/profile")
def profile():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()
    conn.close()

    if student is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("profile.html", student=student)


# Level 4: Update course using AJAX
@app.route("/update-course", methods=["POST"])
def update_course():
    if "student_id" not in session:
        return jsonify({"error": "Please log in first."}), 401

    course = request.form.get("course", "")
    allowed_courses = ["Computer Science", "Data Science",
                       "Cloud Computing", "Business Analytics"]

    if course not in allowed_courses:
        return jsonify({"error": "Invalid course selected."}), 400

    conn = get_db()
    conn.execute(
        "UPDATE students SET course = ? WHERE id = ?",
        (course, session["student_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({
        "message": f"Course updated to: {course}",
        "course": course
    })


# Level 3: Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
