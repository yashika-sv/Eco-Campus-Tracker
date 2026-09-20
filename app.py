from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "eco-campus-secret-key"

DATABASE = os.path.join(os.path.dirname(__file__), "database.db")


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not email or not password:
            flash("Please enter email and password.")
            return redirect(url_for("login"))

        if "@" not in email or "." not in email:
              flash("Please enter a valid email address.")
              return redirect(url_for("login"))

        connection = get_db_connection()

        student = connection.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if student and check_password_hash(student["password"], password):

            session["student_id"] = student["id"]

            flash("Login successful!")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()

    connection.close()

    if student is None:
        session.clear()
        flash("Student account not found.")
        return redirect(url_for("login"))

    activity_count = 0
    pending_count = 0

    return render_template(
        "dashboard.html",
        student=student,
        activity_count=activity_count,
        pending_count=pending_count
    )

@app.route("/profile")
def profile():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()

    connection.close()

    if student is None:
        session.clear()
        flash("Student account not found.")
        return redirect(url_for("login"))

    return render_template("profile.html", student=student)

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()
        flash("Student account not found.")
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()

        if not name or not email:
            connection.close()
            flash("Name and email cannot be empty.")
            return redirect(url_for("edit_profile"))

        if len(name) < 2:
            connection.close()
            flash("Name must contain at least 2 characters.")
            return redirect(url_for("edit_profile"))

        if "@" not in email or "." not in email:
            connection.close()
            flash("Please enter a valid email address.")
            return redirect(url_for("edit_profile"))

        existing_student = connection.execute(
            "SELECT id FROM students WHERE email = ? AND id != ?",
            (email, session["student_id"])
        ).fetchone()

        if existing_student:
            connection.close()
            flash("This email is already registered.")
            return redirect(url_for("edit_profile"))

        connection.execute(
            """
            UPDATE students
            SET name = ?, email = ?
            WHERE id = ?
            """,
            (name, email, session["student_id"])
        )

        connection.commit()
        connection.close()

        flash("Profile updated successfully.")
        return redirect(url_for("profile"))

    connection.close()

    return render_template("edit_profile.html", student=student)


@app.route("/profile/change-password", methods=["GET", "POST"])
def change_password():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()
        flash("Student account not found.")
        return redirect(url_for("login"))

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not current_password or not new_password or not confirm_password:
            connection.close()
            flash("Please fill in all password fields.")
            return redirect(url_for("change_password"))

        if not check_password_hash(student["password"], current_password):
            connection.close()
            flash("Current password is incorrect.")
            return redirect(url_for("change_password"))

        if len(new_password) < 6:
            connection.close()
            flash("New password must contain at least 6 characters.")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            connection.close()
            flash("New passwords do not match.")
            return redirect(url_for("change_password"))

        if new_password == current_password:
            connection.close()
            flash("New password must be different from the current password.")
            return redirect(url_for("change_password"))

        hashed_password = generate_password_hash(new_password)

        connection.execute(
            """
            UPDATE students
            SET password = ?
            WHERE id = ?
            """,
            (hashed_password, session["student_id"])
        )

        connection.commit()
        connection.close()

        flash("Password changed successfully.")
        return redirect(url_for("profile"))

    connection.close()

    return render_template("change_password.html")


@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")
    return redirect(url_for("login"))



@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not name or not email or not password or not confirm_password:
            flash("Please fill in all fields.")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return redirect(url_for("register"))

        connection = get_db_connection()

        existing_student = connection.execute(
            "SELECT id FROM students WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_student:
            connection.close()
            flash("An account with this email already exists.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        connection.execute(
            """
            INSERT INTO students (name, email, password, eco_points)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, hashed_password, 0)
        )

        connection.commit()
        connection.close()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)