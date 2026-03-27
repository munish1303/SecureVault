# Secure Vault Password Manager

Secure Vault is a full-stack Flask password manager designed to store user credentials securely using modern security practices. It combines strong authentication, encrypted password storage, password generation, password strength analysis, activity logging, session protection, and a cybersecurity-inspired graphical user interface.

The project is built for academic and demonstration purposes, but it follows practical security principles such as salted password hashing, symmetric encryption, brute-force protection, authenticated password reveal, and database query parameterization. The interface has been designed as a command-center style dashboard so users can manage credentials in a cleaner and more professional environment.

## Quick Start

If you just want to run the project quickly on Windows PowerShell:

```powershell
git clone <your-repository-url>
cd <your-project-folder>
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_SECRET_KEY="replace-this-with-a-long-random-secret"
py -3 run.py
```

Then open:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

Demo login:

- Username: `demo_user`
- Master Password: `DemoVault@2026!`

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Security Design](#security-design)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [How to Clone the Project](#how-to-clone-the-project)
- [How to Run the Project](#how-to-run-the-project)
- [Windows Setup](#windows-setup)
- [Linux and macOS Setup](#linux-and-macos-setup)
- [Demo Account](#demo-account)
- [How the Application Works](#how-the-application-works)
- [Main Pages in the UI](#main-pages-in-the-ui)
- [Screenshots](#screenshots)
- [Database Information](#database-information)
- [Important Notes for Other Users](#important-notes-for-other-users)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## Project Overview

This application allows a user to create a secure account using a master password, log in to a protected vault, and store website or application credentials safely. The master password itself is never stored in plain text. Instead, it is hashed with bcrypt. Each stored credential password is encrypted before being written to the database, and decryption only happens after authentication and master-password verification.

The app also includes:

- user registration and login
- secure session-based authentication
- add, view, update, and delete credential records
- password generator with configurable options
- password strength checker
- recent activity logging
- suspicious activity alerts
- test security alert trigger for UI demonstration
- automatic demo-data seeding
- responsive cyber-command-center style interface

## Key Features

### 1. User Authentication

- Register with a username and master password
- Login with hashed password verification using bcrypt
- Logout securely using Flask session handling
- Temporary lockout after multiple failed login attempts
- Session timeout after inactivity

### 2. Encrypted Password Storage

- Store credentials for websites and applications
- Encrypt stored passwords using `cryptography.Fernet`
- Use a key derived from the user's master password instead of storing an encryption key in plain text
- Require master-password confirmation before sensitive password actions

### 3. Password Management

- Add a new credential
- Reveal a credential securely after verification
- Edit existing credentials
- Delete stored credentials
- Seed sample credentials for new users and the demo account

### 4. Password Utility Tools

- Generate strong passwords with configurable length and character rules
- Analyze password strength based on character variety, length, and entropy estimate

### 5. Activity Logging and Alerts

- Log important actions such as login success, failed login, credential addition, password reveal, update, delete, and logout
- Detect suspicious behavior patterns
- Display security alerts in the dashboard
- Trigger a manual test alert for demonstration purposes

### 6. Professional Graphical User Interface

- Secure login and registration screens
- Command-center style dashboard
- Sidebar navigation for quick access
- Dedicated tools page for generation and strength analysis
- Clean, dark, cybersecurity-inspired visual design

## Security Design

This project was designed to demonstrate secure password management practices.

### Password Hashing

Master passwords are hashed using `bcrypt`, which automatically includes a salt. This protects stored passwords from being recovered directly from the database.

### Encryption of Stored Credentials

Saved website or application passwords are encrypted using `Fernet` symmetric encryption from the `cryptography` library.

### Derived Encryption Key

The encryption key is not stored in plain text. Instead, the application derives the encryption key dynamically from:

- the user’s master password
- a per-user random salt
- PBKDF2-HMAC-SHA256 key derivation

This means even if the database is exposed, encrypted credential values cannot be directly decrypted without the correct master password.

### SQL Injection Prevention

All database queries use parameterized SQLite statements rather than unsafe string concatenation.

### Brute-Force Protection

The application tracks failed login attempts and applies temporary account lockouts if too many failed attempts occur in a short period.

### Session Protection

Flask session management is used to protect authenticated routes. Sessions expire automatically after a defined inactivity period.

### Sensitive Action Verification

Viewing, updating, or deleting credentials requires the master password to be re-entered for an additional layer of protection.

## Technology Stack

### Backend

- Python
- Flask
- SQLite

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2 templates

### Security Libraries

- `bcrypt`
- `cryptography`

## Project Structure

```text
SSS Assignment/
  backend/
    app.py
    auth.py
    encryption.py
    models.py
    seeder.py
    utils.py
    __init__.py
  frontend/
    templates/
      base.html
      login.html
      register.html
      dashboard.html
      add_password.html
      edit_password.html
      tools.html
    static/
      styles.css
      app.js
  database.db
  requirements.txt
  run.py
  README.md
```

### File Roles

- `backend/app.py`: Main Flask routes and application flow
- `backend/auth.py`: Authentication logic and decorators
- `backend/encryption.py`: Key derivation, encryption, and decryption helpers
- `backend/models.py`: SQLite database layer and query methods
- `backend/seeder.py`: Demo account and sample credential seeding
- `backend/utils.py`: Password generation and strength analysis helpers
- `frontend/templates/`: HTML templates rendered by Flask
- `frontend/static/styles.css`: Main styling for the application UI
- `frontend/static/app.js`: Client-side interactions such as copy and utility actions
- `run.py`: Application entry point

## How to Clone the Project

If this project is uploaded to GitHub or another Git hosting platform, another user can clone it using:

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

Example:

```bash
git clone https://github.com/your-username/secure-vault-password-manager.git
cd secure-vault-password-manager
```

If you are submitting the project as a folder instead of a Git repository, the other user can simply copy the project folder to their machine and run the same setup steps below.

## How to Run the Project

You can run the project on Windows, Linux, or macOS. The steps are almost the same, with small differences in virtual environment activation and environment variable syntax.

## Windows Setup

### 1. Install Python

Install Python 3.10 or later from the official Python website:

[https://www.python.org/downloads/](https://www.python.org/downloads/)

During installation, make sure to enable the option to add Python to `PATH`.

### 2. Open the project folder

```powershell
cd "C:\path\to\your\project"
```

### 3. Create a virtual environment

```powershell
py -3 -m venv .venv
```

If `py` does not work, use:

```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

### 6. Set the Flask secret key

```powershell
$env:FLASK_SECRET_KEY="replace-this-with-a-long-random-secret"
```

Example:

```powershell
$env:FLASK_SECRET_KEY="secure-vault-demo-secret-2026"
```

### 7. Run the application

```powershell
py -3 run.py
```

If needed, use:

```powershell
python run.py
```

### 8. Open the app in your browser

[http://127.0.0.1:5000](http://127.0.0.1:5000)

## Linux and macOS Setup

### 1. Install Python

Make sure Python 3.10 or later is installed:

```bash
python3 --version
```

### 2. Open the project folder

```bash
cd /path/to/your/project
```

### 3. Create a virtual environment

```bash
python3 -m venv .venv
```

### 4. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Set the Flask secret key

```bash
export FLASK_SECRET_KEY="replace-this-with-a-long-random-secret"
```

### 7. Run the application

```bash
python3 run.py
```

### 8. Open the app in your browser

[http://127.0.0.1:5000](http://127.0.0.1:5000)

## Demo Account

The application seeds a demo user on first run and can also seed starter credentials for new accounts.

### Demo Login

- Username: `demo_user`
- Master Password: `DemoVault@2026!`

### Seeded Sample Credentials

The sample encrypted records include entries such as:

- GitHub
- Gmail
- Netflix
- AWS Console
- LinkedIn

These are provided for demonstration and testing of the vault interface.

## How the Application Works

### Registration Flow

1. A user creates an account with a username and master password.
2. The master password is hashed with bcrypt.
3. A unique salt for encryption key derivation is generated for the user.
4. The user record is stored in SQLite.
5. Starter encrypted credentials may be seeded for the new user.

### Login Flow

1. The user enters a username and master password.
2. The application verifies the password against the bcrypt hash.
3. If valid, a Flask session is created.
4. Recent login activity is logged.
5. If the account has no stored credentials, sample credentials can be seeded automatically.

### Credential Storage Flow

1. The user submits a site name, account username, and password.
2. The application derives an encryption key from the master password.
3. The password is encrypted with Fernet.
4. The encrypted value is stored in the database.

### Credential Reveal Flow

1. The user requests to reveal a stored password.
2. The application asks for the master password again.
3. The key is derived again from that password.
4. The stored encrypted password is decrypted only for that action.
5. The reveal event is logged.

## Main Pages in the UI

### Login Page

Allows existing users to sign in securely.

### Register Page

Allows a new user to create an account with a master password.

### Dashboard

Displays:

- stored credential inventory
- recent activity logs
- security alert information
- current session information
- quick navigation actions

### Add Password Page

Used to securely add a new credential to the vault.

### Edit Password Page

Used to update an existing saved credential after authentication.

### Tools Page

Includes:

- password generator
- password strength analyzer

## Screenshots

The README is prepared for screenshots so the project looks complete when shared. I do not have exported image files for the current UI inside this workspace, so the section below describes exactly what should be shown and where to place images once you capture them.

If you want to add real screenshots later, create a folder such as `docs/screenshots/` and save images there. Then replace the placeholder text below with Markdown image tags.

Suggested screenshot list:

- `login-page.png`
  Show the secure access login screen.
- `register-page.png`
  Show the user registration interface.
- `dashboard.png`
  Show the command-center dashboard with stored credentials, activity, and alerts.
- `add-password.png`
  Show the credential creation form.
- `tools-page.png`
  Show the password generator and strength checker.
- `security-alert.png`
  Show the test alert visible in the dashboard.

Example Markdown if you add screenshot files later:

```md
![Login Page](docs/screenshots/login-page.png)
![Dashboard](docs/screenshots/dashboard.png)
```

Recommended screenshot captions:

- Login Page: Secure sign-in interface for registered users.
- Register Page: New-user registration with master-password creation.
- Dashboard: Cybersecurity command-center view of vault activity and records.
- Add Password Page: Secure form for storing a new encrypted credential.
- Tools Page: Utility panel for strong password generation and analysis.
- Security Alert: Demonstration alert shown for testing the monitoring UI.

## Database Information

The project uses SQLite and creates `database.db` automatically on first run.

### Main Tables

#### Users

- `id`
- `username`
- `password_hash`
- `key_salt`
- lockout and security-related metadata

#### Passwords

- `id`
- `user_id`
- `site`
- `username`
- `encrypted_password`
- `notes`
- timestamps

#### Logs

- `id`
- `user_id`
- `action`
- `details`
- `timestamp`

## Important Notes for Other Users

- The database file is generated locally and should not be shared with real secrets inside it.
- The included demo credentials are only sample records for testing.
- Replace the demo secret key with a strong random production key.
- For production deployment, do not use Flask's built-in development server.
- For production deployment, place the app behind HTTPS and a production-grade WSGI server.
- If you want a clean database, delete `database.db` and restart the app.

## Troubleshooting

### The app does not start

Make sure Python is installed and available in your terminal:

```bash
python --version
```

or

```bash
python3 --version
```

or on Windows:

```powershell
py -3 --version
```

### Dependencies fail to install

Upgrade `pip` and try again:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Linux or macOS, if `python` maps to Python 2, use:

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### PowerShell blocks script execution

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### The browser shows old styles

Do a hard refresh:

```text
Ctrl + F5
```

### The database needs to be reset

Close the app, delete `database.db`, and run the project again.

## Future Improvements

Possible future extensions for this project include:

- two-factor authentication
- secure export and import of credentials
- password sharing with access controls
- stronger anomaly detection rules
- email alert notifications
- audit filtering and reporting tools
- production deployment configuration
- role-based administrative controls

---

If you are submitting this project publicly, update the example Git clone URL in this README to match your real repository link and add real screenshots in a `docs/screenshots/` folder for the best presentation.
