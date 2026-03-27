import os
from datetime import timedelta

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from .auth import AuthService
from .encryption import EncryptionManager
from .models import DatabaseManager
from .seeder import DemoSeeder
from .utils import PasswordTools, format_timestamp, login_required


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")


class PasswordManagerApp:
    def __init__(self) -> None:
        self.app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
        self.app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32).hex()
        self.app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)
        self.db = DatabaseManager()
        self.auth_service = AuthService(self.db)
        self.seeder = DemoSeeder(self.db, self.auth_service)
        self.seeder.seed_demo_data()
        self._register_filters()
        self._register_routes()

    def _register_filters(self) -> None:
        self.app.jinja_env.filters["datetime"] = format_timestamp

    def _touch_session(self) -> None:
        session.permanent = True
        session["last_seen"] = str(os.times())

    def _register_routes(self) -> None:
        app = self.app

        @app.before_request
        def refresh_session() -> None:
            if "user_id" in session:
                self._touch_session()

        @app.route("/")
        def index():
            if "user_id" in session:
                return redirect(url_for("dashboard"))
            return redirect(url_for("login"))

        @app.route("/register", methods=["GET", "POST"])
        def register():
            if request.method == "POST":
                username = request.form.get("username", "").strip()
                master_password = request.form.get("master_password", "")
                confirm_password = request.form.get("confirm_password", "")

                if master_password != confirm_password:
                    flash("Master passwords do not match.", "danger")
                    return redirect(url_for("register"))

                result, message = self.auth_service.register_user(username, master_password)
                if result:
                    user = self.db.get_user_by_username(username)
                    self.seeder.seed_user_credentials(user, master_password)
                flash(message, "success" if result else "danger")
                return redirect(url_for("login" if result else "register"))

            return render_template("register.html")

        @app.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                username = request.form.get("username", "").strip()
                master_password = request.form.get("master_password", "")

                result, message, user = self.auth_service.verify_login(username, master_password)
                if result and user:
                    self.seeder.seed_user_credentials(user, master_password)
                    session.clear()
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    self._touch_session()
                    flash(message, "success")
                    return redirect(url_for("dashboard"))

                flash(message, "danger")
                return redirect(url_for("login"))

            return render_template("login.html")

        @app.route("/logout")
        @login_required
        def logout():
            self.db.log_event(session.get("user_id"), "LOGOUT", "User logged out.")
            session.clear()
            flash("You have been logged out.", "info")
            return redirect(url_for("login"))

        @app.route("/dashboard")
        @login_required
        def dashboard():
            user_id = session["user_id"]
            alerts = self.db.suspicious_events(user_id)
            if session.get("show_test_alert"):
                alerts.insert(
                    0,
                    {
                        "level": "high",
                        "message": "Test alert injected for UI verification. This is a simulated security event.",
                    },
                )
            return render_template(
                "dashboard.html",
                entries=self.db.get_passwords_for_user(user_id),
                logs=self.db.recent_logs(user_id),
                alerts=alerts,
                active_page="dashboard",
            )

        @app.route("/alerts/test", methods=["POST"])
        @login_required
        def trigger_test_alert():
            session["show_test_alert"] = True
            self.db.log_event(session["user_id"], "SECURITY_ALERT", "Test alert manually triggered for UI verification.")
            flash("Test security alert triggered.", "warning")
            return redirect(url_for("dashboard"))

        @app.route("/alerts/test/clear", methods=["POST"])
        @login_required
        def clear_test_alert():
            session.pop("show_test_alert", None)
            flash("Test security alert cleared.", "info")
            return redirect(url_for("dashboard"))

        @app.route("/passwords/add", methods=["GET", "POST"])
        @login_required
        def add_password():
            if request.method == "POST":
                site = request.form.get("site", "").strip()
                entry_username = request.form.get("entry_username", "").strip()
                entry_password = request.form.get("entry_password", "")
                notes = request.form.get("notes", "").strip()
                master_password = request.form.get("master_password", "")

                if not site or not entry_username or not entry_password:
                    flash("Site, username, and password are required.", "danger")
                    return redirect(url_for("add_password"))

                if not self.auth_service.verify_master_password(session["user_id"], master_password):
                    self.db.log_event(session["user_id"], "PASSWORD_ADD_FAILED", "Master password verification failed.")
                    flash("Master password verification failed.", "danger")
                    return redirect(url_for("add_password"))

                user = self.db.get_user_by_id(session["user_id"])
                encrypted_password = EncryptionManager.encrypt_password(entry_password, master_password, user["encryption_salt"])
                self.db.add_password(session["user_id"], site, entry_username, encrypted_password, notes)
                self.db.log_event(session["user_id"], "PASSWORD_ADDED", f"Credential stored for {site}.")
                flash("Credential stored securely.", "success")
                return redirect(url_for("dashboard"))

            return render_template("add_password.html", active_page="add")

        @app.route("/passwords/<int:entry_id>/view", methods=["POST"])
        @login_required
        def view_password(entry_id: int):
            master_password = request.form.get("master_password", "")
            entry = self.db.get_password_entry(entry_id, session["user_id"])

            if not entry:
                return jsonify({"ok": False, "message": "Entry not found."}), 404
            if not self.auth_service.verify_master_password(session["user_id"], master_password):
                self.db.log_event(session["user_id"], "PASSWORD_VIEW_FAILED", f"Master password verification failed for entry {entry_id}.")
                return jsonify({"ok": False, "message": "Master password verification failed."}), 403

            user = self.db.get_user_by_id(session["user_id"])
            try:
                plaintext = EncryptionManager.decrypt_password(entry["encrypted_password"], master_password, user["encryption_salt"])
            except ValueError:
                self.db.log_event(session["user_id"], "PASSWORD_VIEW_FAILED", f"Decryption failed for entry {entry_id}.")
                return jsonify({"ok": False, "message": "Unable to decrypt password."}), 403

            self.db.log_event(session["user_id"], "PASSWORD_VIEWED", f"Credential viewed for {entry['site']}.")
            return jsonify({"ok": True, "password": plaintext})

        @app.route("/passwords/<int:entry_id>/edit", methods=["GET", "POST"])
        @login_required
        def edit_password(entry_id: int):
            entry = self.db.get_password_entry(entry_id, session["user_id"])
            if not entry:
                flash("Credential not found.", "danger")
                return redirect(url_for("dashboard"))

            if request.method == "POST":
                site = request.form.get("site", "").strip()
                entry_username = request.form.get("entry_username", "").strip()
                entry_password = request.form.get("entry_password", "")
                notes = request.form.get("notes", "").strip()
                master_password = request.form.get("master_password", "")

                if not site or not entry_username or not entry_password:
                    flash("All required fields must be completed.", "danger")
                    return redirect(url_for("edit_password", entry_id=entry_id))
                if not self.auth_service.verify_master_password(session["user_id"], master_password):
                    self.db.log_event(session["user_id"], "PASSWORD_UPDATE_FAILED", f"Master password verification failed for entry {entry_id}.")
                    flash("Master password verification failed.", "danger")
                    return redirect(url_for("edit_password", entry_id=entry_id))

                user = self.db.get_user_by_id(session["user_id"])
                encrypted_password = EncryptionManager.encrypt_password(entry_password, master_password, user["encryption_salt"])
                self.db.update_password(entry_id, session["user_id"], site, entry_username, encrypted_password, notes)
                self.db.log_event(session["user_id"], "PASSWORD_UPDATED", f"Credential updated for {site}.")
                flash("Credential updated.", "success")
                return redirect(url_for("dashboard"))

            return render_template("edit_password.html", entry=entry, active_page="dashboard")

        @app.route("/passwords/<int:entry_id>/delete", methods=["POST"])
        @login_required
        def delete_password(entry_id: int):
            entry = self.db.get_password_entry(entry_id, session["user_id"])
            master_password = request.form.get("master_password", "")

            if not entry:
                flash("Credential not found.", "danger")
                return redirect(url_for("dashboard"))
            if not self.auth_service.verify_master_password(session["user_id"], master_password):
                self.db.log_event(session["user_id"], "PASSWORD_DELETE_FAILED", f"Master password verification failed for entry {entry_id}.")
                flash("Master password verification failed.", "danger")
                return redirect(url_for("dashboard"))

            self.db.delete_password(entry_id, session["user_id"])
            self.db.log_event(session["user_id"], "PASSWORD_DELETED", f"Credential deleted for {entry['site']}.")
            flash("Credential deleted.", "info")
            return redirect(url_for("dashboard"))

        @app.route("/tools")
        @login_required
        def tools():
            return render_template("tools.html", active_page="tools")

        @app.route("/api/generate-password", methods=["POST"])
        @login_required
        def generate_password():
            payload = request.get_json(silent=True) or {}
            try:
                generated = PasswordTools.generate_password(
                    int(payload.get("length", 16)),
                    bool(payload.get("use_uppercase", True)),
                    bool(payload.get("use_numbers", True)),
                    bool(payload.get("use_symbols", True)),
                )
            except ValueError as exc:
                return jsonify({"ok": False, "message": str(exc)}), 400

            return jsonify({"ok": True, "password": generated, "analysis": PasswordTools.analyze_strength(generated)})

        @app.route("/api/analyze-password", methods=["POST"])
        @login_required
        def analyze_password():
            payload = request.get_json(silent=True) or {}
            return jsonify({"ok": True, "analysis": PasswordTools.analyze_strength(payload.get("password", ""))})


password_manager = PasswordManagerApp()
app = password_manager.app


if __name__ == "__main__":
    app.run(debug=True)


