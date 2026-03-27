Project Report

## Student Details
- Name 1 - Roll Number
- Name 2 - Roll Number
- Name 3 - Roll Number

## Project Title
Secure Vault: Secure Password Manager with Encryption, Authentication, Logging, and Cybersecurity Command Center UI

## Abstract
This project is a secure password manager application built with Python Flask, SQLite, bcrypt, and the cryptography library. The goal of the system is to help a user safely store, manage, retrieve, and protect website and application passwords through strong authentication, hashed master credentials, symmetric encryption, secure session handling, password generation, password strength analysis, activity logging, and security alerts.

The application provides a graphical web interface with separate pages for login, registration, dashboard monitoring, credential management, and security tools. The dashboard was redesigned into a cybersecurity command center style so the user can review stored credentials, activity logs, alerts, and protection status from one operational view. The system also supports starter demo credentials, secure reveal and update flows that require master password verification, suspicious-login alerting, and a manual test alert trigger for UI verification.

This report explains the problem statement, objectives, architecture, implementation details, security model, functional modules, testing approach, strengths, limitations, and future enhancements of the project.

## 1. Problem Statement
Modern users manage many website and application accounts, and weak password habits often lead to password reuse, unsafe storage, forgotten credentials, and poor visibility into suspicious account activity. Many beginner users also do not clearly understand the difference between hashing, encryption, session handling, and secure password generation.

The problem addressed in this project is how to build a password manager application that:
- stores user master passwords securely using salted hashing,
- encrypts stored credentials before saving them to the database,
- allows controlled password retrieval only after verification,
- supports password generation and strength analysis,
- logs security-relevant events,
- alerts the user about suspicious activity,
- and presents all of these operations in a clean graphical interface suitable for an academic project.

The system should also be modular, secure by design, and easy to understand for learning and demonstration purposes.

## 2. Objectives
The main objectives of this project are:
- To build a complete password manager using Python Flask and SQLite.
- To store master passwords securely using bcrypt hashing.
- To encrypt stored website and application passwords using Fernet encryption.
- To derive the encryption key from the user master password instead of storing a plaintext key.
- To support secure user registration, login, logout, and session-based access control.
- To require master password verification before revealing, updating, or deleting credentials.
- To generate strong random passwords with configurable options.
- To analyze password strength using length, entropy, and character variety.
- To log important actions such as login attempts and password operations.
- To generate security alerts for suspicious login patterns and other risky activity.
- To organize the code modularly using OOP principles.
- To provide a professional graphical user interface.

## 3. Proposed Solution
The proposed solution is a secure web application called Secure Vault. It uses a modular Flask backend with separate modules for authentication, encryption, database handling, utility functions, and demo seeding. The frontend uses HTML, CSS, and JavaScript templates to provide a multi-page user interface.

The system is divided into the following main pages:
- Login page: authenticates the user with a username and master password.
- Register page: creates a new user account and prepares secure vault storage.
- Dashboard page: shows stored credentials, recent activity, security alerts, protection status, and operational controls.
- Add Credential page: lets the user store a new encrypted password.
- Edit Credential page: allows secure update of an existing encrypted credential.
- Security Tools page: provides password generation and strength analysis.

The system uses SQLite for local persistence. It also includes starter seeded credentials for testing and a test alert trigger for verifying the alert interface.

## 4. Technology Stack
The following technologies were used in this project:
- Python for application logic
- Flask for the web framework and routing
- SQLite for local database storage
- bcrypt for salted password hashing
- cryptography library with Fernet for symmetric encryption
- PBKDF2HMAC with SHA-256 for key derivation
- HTML, CSS, and JavaScript for the graphical user interface

### Why this stack was chosen
This stack was chosen because it is practical, lightweight, easy to explain, and suitable for academic submission. Flask allows the application to keep backend routing and frontend templates simple. SQLite removes the setup complexity of a separate database server. bcrypt provides trusted password hashing, while the cryptography library provides strong modern encryption primitives. The overall stack is enough to demonstrate real security concepts without making the project too difficult to run.

## 5. System Architecture
The application follows a modular layered architecture. Each part of the system has a clear job.

### 5.1 High-Level Architecture
1. The user interacts with the web interface.
2. Flask routes receive requests from the browser.
3. The authentication, database, encryption, and utility classes process the request.
4. SQLite stores or retrieves user records, encrypted credentials, and logs.
5. The system returns updated data to the interface.

### 5.2 Main Modules
### 1. UI Layer
The UI layer contains the templates and static assets shown to the user. It includes:
- secure access pages,
- command center dashboard,
- credential forms,
- password generator panel,
- strength checker panel,
- reveal and delete confirmation modals,
- activity feed,
- and security alert panels.

### 2. Route Layer
The Flask route layer handles:
- registration,
- login,
- logout,
- dashboard rendering,
- credential add, view, edit, and delete actions,
- password generation API,
- password analysis API,
- and test alert triggering and clearing.

### 3. Security and Service Layer
The service layer includes:
- `AuthService` for registration and login validation,
- `EncryptionManager` for key derivation and password encryption/decryption,
- `PasswordTools` for generation and strength analysis,
- `DemoSeeder` for starter data,
- and utility decorators for protected access.

### 4. Storage Layer
The storage layer is handled by `DatabaseManager` and SQLite. It stores:
- users,
- encrypted credentials,
- logs,
- failed login counters,
- and lockout timestamps.

This design keeps the project modular and easier to document.

## 6. Functional Modules
### 6.1 User Authentication Module
The application includes registration, login, and logout. During registration, the master password is hashed with bcrypt and never stored in plaintext. During login, the entered password is verified against the stored hash. Flask sessions are used to maintain authenticated state.

The login process also includes brute-force protection. If too many failed attempts occur, the account is temporarily locked and a security alert is logged.

### 6.2 Password Management Module
This is the core feature of the project. The user can:
- add a new credential,
- view a stored password after master-password confirmation,
- update a credential,
- and delete a credential.

Stored website or app passwords are encrypted before insertion into the database. Revealing, editing, and deleting credentials require re-verification of the master password, even if the user is already logged in.

### 6.3 Dashboard Monitoring Module
The dashboard acts like a secure operations console. It displays:
- number of stored credentials,
- recent activity count,
- alert count,
- protection mode status,
- stored credential inventory,
- audit feed,
- and security posture details.

This page is the main operational view of the system.

### 6.4 Password Generator Module
The tools page includes a generator that can create strong random passwords. The user can configure:
- password length,
- uppercase letters,
- numbers,
- and symbols.

The generated password can also be copied through the UI.

### 6.5 Password Strength Checker Module
The application includes a password strength analyzer that evaluates a password based on:
- length,
- character variety,
- and estimated entropy.

The result is shown as weak, medium, or strong with a visual meter.

### 6.6 Activity Logging Module
The application logs important actions such as:
- successful and failed logins,
- registration,
- logout,
- password add, view, update, and delete actions,
- security alert events,
- and test alert triggering.

These logs are stored in the `logs` table and displayed through the dashboard activity feed.

### 6.7 Security Alerts Module
The system generates alerts for suspicious behavior such as:
- repeated failed logins,
- account lockout periods,
- and unusually frequent password reveal actions.

A manual test alert trigger was also added so the alert UI can be verified during demonstrations.

## 7. Workflow of the System
The basic workflow of the project is:
1. The user opens the application.
2. The user registers or logs in.
3. A secure session is created.
4. The user enters the dashboard command center.
5. The user adds, views, edits, or deletes credentials.
6. Passwords are encrypted before storage and decrypted only after verification.
7. All important actions are logged.
8. The dashboard displays alerts and activity.
9. The user can open the security tools page to generate or analyze passwords.

## 8. Screenshots
The screenshots section can include the following pages:
- Login page
- Register page
- Dashboard command center
- Add Credential page
- Edit Credential page
- Security Tools page
- Security alert test view

## 9. Implementation Details
### 9.1 UI Design
The UI was redesigned from a basic dashboard layout into a cybersecurity command center interface. The final design focuses on:
- a clear left-side navigation rail,
- a command-center style header,
- operational metric panels,
- a tactical credential table,
- a right-side alert and audit rail,
- and secure intake and utility console pages.

This design was chosen to make the application look more professional and distinct from a standard student CRUD interface.

### 9.2 State Management and Database Logic
The application uses SQLite for persistent state. The main database file is `database.db`. It stores user accounts, encrypted credentials, and logs. The database layer uses parameterized queries to reduce SQL injection risk.

The session state is handled through Flask sessions, while demo alert visualization uses a temporary session flag.

### 9.3 Alert Detection Logic
The alert detection logic checks for conditions such as:
- multiple failed login attempts in a short time window,
- active account lockout periods,
- and unusually frequent password reveal actions.

These checks are implemented through database lookups and recent log analysis.

### 9.4 Security Logic
The security flow is implemented as follows:
1. Hash the master password with bcrypt.
2. Generate a per-user encryption salt.
3. Derive a Fernet key using PBKDF2HMAC with the master password and salt.
4. Encrypt stored credentials before database insertion.
5. Re-derive the key during secure reveal.
6. Require session authentication and master-password confirmation for sensitive actions.

## 10. Security Features
The main security features of the project are:
- bcrypt salted password hashing
- PBKDF2-based key derivation
- Fernet symmetric encryption for stored credentials
- no plaintext encryption key storage
- Flask session-based authentication
- brute-force protection with temporary lockout
- suspicious login detection
- security alert generation
- secure password generation
- password strength analysis
- activity logging
- parameterized SQLite queries
- secure reveal, update, and delete verification
- clipboard copy support with timeout clearing attempt

These features make the project both functional and security-focused.

## 11. Security Analysis
### 11.1 Strengths of the System
- The system separates hashing and encryption correctly.
- It does not store the vault encryption key in plaintext.
- Sensitive actions require re-verification of the master password.
- Repeated login failures are monitored and limited.
- The architecture is modular and easier to maintain.
- The UI clearly presents alerts, audit activity, and credential operations.
- The project demonstrates both usability and security concepts in one system.

### 11.2 Limitations
- The application uses SQLite, which is suitable for a local project but not ideal for large multi-user production use.
- CSRF protection is not fully implemented.
- Two-factor authentication is not included.
- Clipboard clearing is best-effort and depends on browser behavior.
- The current system is designed for educational and local use rather than large-scale deployment.

### 11.3 Risk Discussion
If this project were extended into a production system, additional hardening would be required, such as:
- CSRF protection,
- stronger secret management,
- HTTPS-only deployment,
- production WSGI deployment,
- rate limiting at the application edge,
- role-based access control,
- multi-factor authentication,
- secure export and import,
- and database scaling beyond local SQLite.

Even with these limitations, the project strongly meets its academic goal because it demonstrates secure password storage, encryption, session control, and cybersecurity-aware UI design in a working system.

## 12. Testing and Verification
The project can be tested through the following checks:
- registration and login verification,
- logout verification,
- failed login and lockout verification,
- credential add, view, update, and delete actions,
- password generator testing,
- password strength checker testing,
- activity log verification,
- suspicious alert verification,
- manual test alert verification,
- dashboard route verification,
- and page-level UI verification.

The current project does not include a dedicated automated test suite. Verification is mainly manual and feature-oriented.

## 13. Project Structure Summary
The source code is organized in a modular way. The main files and folders are:
- `backend/app.py` for Flask application setup and routes
- `backend/auth.py` for registration and login services
- `backend/encryption.py` for key derivation and Fernet encryption
- `backend/models.py` for SQLite access and alert logic
- `backend/seeder.py` for starter demo credentials
- `backend/utils.py` for password tools and login protection helpers
- `frontend/templates` for HTML pages
- `frontend/static` for CSS and JavaScript assets
- `database.db` for persistent local storage
- `requirements.txt` for dependencies
- `run.py` for running the application
- `README.md` for setup and usage information

This structure makes the project easier to explain, debug, and maintain.

## 14. Conclusion
This project successfully implements a secure password manager application with a graphical user interface. It supports user authentication, encrypted credential storage, controlled password reveal, password generation, password strength analysis, activity logging, and security alerts.

The final system is suitable for academic submission because it is modular, security-focused, visually professional, and practical to run as a local project. It demonstrates important concepts such as hashing, symmetric encryption, key derivation, brute-force protection, session handling, and secure UI design in one complete application.

## 15. Future Enhancements
In the future, the system can be improved by adding:
- two-factor authentication,
- CSRF protection,
- PostgreSQL or cloud database support,
- secure encrypted export and import,
- password breach-check integration,
- role-based access control,
- deployment hardening,
- real-time notifications,
- and cloud-hosted production deployment.

## 16. References
- Flask Documentation
- SQLite Documentation
- bcrypt Documentation
- cryptography Documentation
- PBKDF2 Key Derivation Concepts
- Fernet Symmetric Encryption Concepts
- Basic concepts of password manager security
