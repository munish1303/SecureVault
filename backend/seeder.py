from .encryption import EncryptionManager


class DemoSeeder:
    DEMO_USERNAME = "demo_user"
    DEMO_MASTER_PASSWORD = "DemoVault@2026!"
    DEMO_CREDENTIALS = [
        {
            "site": "GitHub",
            "username": "demo.dev@example.com",
            "password": "Gh!7Aq9#Lm2@Xp4",
            "notes": "Demo developer account for testing reveal and edit flows.",
        },
        {
            "site": "Gmail",
            "username": "demo.mail@example.com",
            "password": "M@il4Secure#2026",
            "notes": "Sample email login saved for dashboard testing.",
        },
        {
            "site": "Netflix",
            "username": "family.demo@example.com",
            "password": "Net!View88#Safe",
            "notes": "Streaming profile example entry.",
        },
        {
            "site": "AWS Console",
            "username": "demo-admin",
            "password": "Aws#Cloud9!Vault",
            "notes": "Cloud admin demo credential. Do not use in production.",
        },
        {
            "site": "LinkedIn",
            "username": "demo.profile@example.com",
            "password": "Link!Career55$Go",
            "notes": "Professional account sample record.",
        },
    ]

    def __init__(self, db, auth_service) -> None:
        self.db = db
        self.auth_service = auth_service

    def seed_user_credentials(self, user, master_password: str) -> None:
        if not user or self.db.count_passwords_for_user(user["id"]) > 0:
            return

        for credential in self.DEMO_CREDENTIALS:
            encrypted_password = EncryptionManager.encrypt_password(
                credential["password"],
                master_password,
                user["encryption_salt"],
            )
            self.db.add_password(
                user["id"],
                credential["site"],
                credential["username"],
                encrypted_password,
                credential["notes"],
            )
            self.db.log_event(user["id"], "PASSWORD_ADDED", f"Starter credential stored for {credential['site']}.")

    def seed_demo_data(self) -> None:
        user = self.db.get_user_by_username(self.DEMO_USERNAME)
        if not user:
            created, _ = self.auth_service.register_user(self.DEMO_USERNAME, self.DEMO_MASTER_PASSWORD)
            if not created:
                return
            user = self.db.get_user_by_username(self.DEMO_USERNAME)

        if not user:
            return

        self.seed_user_credentials(user, self.DEMO_MASTER_PASSWORD)
        self.db.log_event(user["id"], "DEMO_SEED_COMPLETED", "Demo credentials were added automatically.")
