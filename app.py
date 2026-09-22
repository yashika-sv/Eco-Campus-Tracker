from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os


app = Flask(__name__)

app.secret_key = "eco-campus-secret-key"

SESSION_TIMEOUT = timedelta(minutes=30)

DATABASE = os.path.join(os.path.dirname(__file__), "database.db")


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


@app.before_request
def check_session_timeout():

    if "student_id" not in session:
        return

    last_activity = session.get("last_activity")

    if last_activity:
        last_activity_time = datetime.fromisoformat(last_activity)

        if datetime.now() - last_activity_time > SESSION_TIMEOUT:
            session.clear()
            flash("Your session has expired. Please login again.")
            return redirect(url_for("login"))

    session["last_activity"] = datetime.now().isoformat()


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

        if student is None:
            connection.close()
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        # Check temporary login lock
        if student["locked_until"]:
            locked_until = datetime.fromisoformat(student["locked_until"])

            if datetime.now() < locked_until:
                remaining_seconds = int(
                    (locked_until - datetime.now()).total_seconds()
                )

                remaining_minutes = max(1, (remaining_seconds + 59) // 60)

                connection.close()

                flash(
                    f"Too many failed login attempts. "
                    f"Please try again in about {remaining_minutes} minute(s)."
                )

                return redirect(url_for("login"))

            # Lock period has ended
            connection.execute(
                """
                UPDATE students
                SET failed_attempts = 0,
                    locked_until = NULL
                WHERE id = ?
                """,
                (student["id"],)
            )

            connection.commit()

            student = connection.execute(
                "SELECT * FROM students WHERE id = ?",
                (student["id"],)
            ).fetchone()

        # Check password
        if check_password_hash(student["password"], password):

            if student["account_status"] != "Active":
                connection.close()
                flash(
                    "Your account is inactive. "
                    "Please contact the administrator."
                )
                return redirect(url_for("login"))

            from datetime import datetime

            last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            connection.execute(
                """
                UPDATE students
                SET last_login = ?,
                    failed_attempts = 0,
                    locked_until = NULL
                WHERE id = ?
                """,
                (last_login, student["id"])
            )

            connection.commit()
            connection.close()

            session["student_id"] = student["id"]
            session["last_activity"] = datetime.now().isoformat()

            flash("Login successful!")
            return redirect(url_for("dashboard"))

        # Wrong password
        failed_attempts = student["failed_attempts"] + 1

        if failed_attempts >= 5:

            locked_until = datetime.now() + timedelta(minutes=5)

            connection.execute(
                """
                UPDATE students
                SET failed_attempts = ?,
                    locked_until = ?
                WHERE id = ?
                """,
                (
                    failed_attempts,
                    locked_until.isoformat(),
                    student["id"]
                )
            )

            connection.commit()
            connection.close()

            flash(
                "Too many failed login attempts. "
                "Your account is locked for 5 minutes."
            )

            return redirect(url_for("login"))

        connection.execute(
            """
            UPDATE students
            SET failed_attempts = ?
            WHERE id = ?
            """,
            (failed_attempts, student["id"])
        )

        connection.commit()
        connection.close()

        attempts_remaining = 5 - failed_attempts

        flash(
            f"Invalid email or password. "
            f"{attempts_remaining} attempt(s) remaining."
        )

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


@app.route("/eco-goal", methods=["GET", "POST"])
def eco_goal():

    if "student_id" not in session:
        flash("Please login to access your eco goal.")
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

        goal_value = request.form.get("eco_goal", "").strip()

        if not goal_value:
            connection.close()
            flash("Please enter an Eco Point goal.")
            return redirect(url_for("eco_goal"))

        try:
            goal_value = int(goal_value)
        except ValueError:
            connection.close()
            flash("Eco Goal must be a valid number.")
            return redirect(url_for("eco_goal"))

        if goal_value < 10 or goal_value > 10000:
            connection.close()
            flash("Eco Goal must be between 10 and 10,000 points.")
            return redirect(url_for("eco_goal"))

        connection.execute(
            """
            UPDATE students
            SET eco_goal = ?
            WHERE id = ?
            """,
            (goal_value, session["student_id"])
        )

        connection.commit()
        connection.close()

        flash("Your Eco Goal has been updated successfully!")
        return redirect(url_for("eco_goal"))

    eco_goal = student["eco_goal"]

    if eco_goal <= 0:
        progress = 0
    else:
        progress = int(
            (student["eco_points"] / eco_goal) * 100
        )

    progress = min(progress, 100)

    connection.close()

    return render_template(
        "eco_goal.html",
        student=student,
        progress=progress
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


@app.route("/profile/deactivate", methods=["POST"])
def deactivate_account():

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

    connection.execute(
        """
        UPDATE students
        SET account_status = 'Inactive'
        WHERE id = ?
        """,
        (session["student_id"],)
    )

    connection.commit()
    connection.close()

    session.clear()

    flash("Your account has been deactivated.")
    return redirect(url_for("login"))


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

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        if not any(char.isupper() for char in password):
            flash("Password must contain at least one uppercase letter.")
            return redirect(url_for("register"))

        if not any(char.islower() for char in password):
            flash("Password must contain at least one lowercase letter.")
            return redirect(url_for("register"))

        if not any(char.isdigit() for char in password):
            flash("Password must contain at least one number.")
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


# ==========================================
# MEMBER 3: LEADERBOARD ROUTE
# ==========================================
@app.route("/leaderboard")
def leaderboard():
    connection = get_db_connection()

    # Fetch students sorted by highest points
    students = connection.execute(
        "SELECT id, name, eco_points FROM students ORDER BY eco_points DESC"
    ).fetchall()

    connection.close()

    return render_template("leaderboard.html", students=students)


# ==========================================
# MEMBER 3: CHALLENGES ROUTE
# ==========================================
@app.route("/challenges")
def challenges():
    connection = get_db_connection()
    # Fetch all available challenges
    challenges_data = connection.execute("SELECT * FROM challenges").fetchall()
    connection.close()

    return render_template("challenges.html", challenges=challenges_data)


# ==========================================
# MEMBER 3: JOIN CHALLENGE ROUTE
# ==========================================
@app.route("/join_challenge/<int:challenge_id>", methods=["POST"])
def join_challenge(challenge_id):
    # Pretend Student 1 is logged in for testing
    student_id = 1

    connection = get_db_connection()

    # Prevent the student from joining the same challenge twice
    existing = connection.execute(
        "SELECT * FROM challenge_participations WHERE student_id = ? AND challenge_id = ?",
        (student_id, challenge_id)
    ).fetchone()

    if not existing:
        connection.execute(
            "INSERT INTO challenge_participations (student_id, challenge_id) VALUES (?, ?)",
            (student_id, challenge_id)
        )
        connection.commit()

    connection.close()

    # Send them back to the challenges page immediately
    return redirect("/challenges")


if __name__ == "__main__":
    app.run(debug=True)