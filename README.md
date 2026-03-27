# Secure Vault Password Manager

Secure Vault is a Flask-based password manager that uses bcrypt for master password hashing and Fernet encryption with a key derived from the user's master password. The application includes user authentication, encrypted credential storage, password generation, password strength analysis, activity logging, security alerts, clipboard copy with timeout clearing, and session timeout protection.

## Project Structure

```text
/backend
  app.py
  auth.py
  encryption.py
  models.py
  seeder.py
  utils.py
/frontend
  /templates
  /static
/database.db
/requirements.txt
/run.py
```

## Setup Instructions

1. Create and activate a virtual environment.
2. Install the dependencies:

```powershell
pip install -r requirements.txt
```

3. Set a strong Flask secret key before running:

```powershell
$env:FLASK_SECRET_KEY="replace-with-a-random-secret"
```

4. Start the application:

```powershell
python run.py
```

5. Open `http://127.0.0.1:5000` in your browser.

## Demo Data

The app includes starter credentials in two ways:

- A built-in demo account is created on first run.
- Any newly registered account also gets the same starter encrypted credentials automatically.

Demo login:

- Username: `demo_user`
- Master Password: `DemoVault@2026!`

Starter stored passwords include GitHub, Gmail, Netflix, AWS Console, and LinkedIn.

## Security Design

- Master passwords are hashed with `bcrypt` using per-password salts.
- Stored credentials are encrypted with `cryptography.Fernet`.
- The Fernet key is not stored in plaintext. It is derived on demand from the submitted master password using `PBKDF2HMAC` with SHA-256 and a per-user random salt.
- Sensitive actions such as revealing, updating, and deleting credentials require master password re-verification.
- SQLite queries use placeholders to prevent SQL injection.
- Repeated failed login attempts trigger temporary account lockouts and security alerts.
- Flask sessions protect authenticated routes and expire after 15 minutes of inactivity.

## Main Features

- Register, login, logout
- Add, view, update, and delete encrypted credentials
- Password generator with configurable options
- Password strength checker with entropy estimate
- Activity log and suspicious activity alerts
- Clipboard copy with 15-second clearing attempt
- Clean responsive UI with a dark navigation panel

## UI Walkthrough

- Login/Register page: split-screen card layout with guided authentication.
- Dashboard: saved credentials table, security alerts, and recent activity.
- Add/Edit page: secure forms that require master password confirmation.
- Tools page: password generator and real-time strength analyzer.

## Notes

- `database.db` is created automatically on first run.
- For production use, replace the development secret key, disable debug mode, serve over HTTPS, and place Flask behind a hardened production WSGI server.
