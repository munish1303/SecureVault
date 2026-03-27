import math
import secrets
import string
from datetime import datetime
from functools import wraps
from typing import Dict

from flask import flash, redirect, session, url_for


class PasswordTools:
    @staticmethod
    def generate_password(length: int, use_uppercase: bool, use_numbers: bool, use_symbols: bool) -> str:
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase if use_uppercase else ""
        numbers = string.digits if use_numbers else ""
        symbols = "!@#$%^&*()-_=+[]{};:,.<>?" if use_symbols else ""
        pool = lowercase + uppercase + numbers + symbols

        if length < 8:
            raise ValueError("Password length must be at least 8 characters.")
        if not pool:
            raise ValueError("At least one character group must be enabled.")

        required = [secrets.choice(lowercase)]
        if use_uppercase:
            required.append(secrets.choice(uppercase))
        if use_numbers:
            required.append(secrets.choice(numbers))
        if use_symbols:
            required.append(secrets.choice(symbols))

        password_chars = required + [secrets.choice(pool) for _ in range(length - len(required))]
        secrets.SystemRandom().shuffle(password_chars)
        return "".join(password_chars)

    @staticmethod
    def analyze_strength(password: str) -> Dict[str, float | int | str]:
        if not password:
            return {"label": "weak", "score": 0, "entropy": 0}

        alphabet = 0
        if any(char.islower() for char in password):
            alphabet += 26
        if any(char.isupper() for char in password):
            alphabet += 26
        if any(char.isdigit() for char in password):
            alphabet += 10
        if any(not char.isalnum() for char in password):
            alphabet += 32

        entropy = round(len(password) * math.log2(max(alphabet, 1)), 2)
        variety_score = sum(
            [
                any(char.islower() for char in password),
                any(char.isupper() for char in password),
                any(char.isdigit() for char in password),
                any(not char.isalnum() for char in password),
            ]
        )
        score = min(100, int((len(password) * 4) + (variety_score * 12) + (entropy / 2)))

        if len(password) < 10 or variety_score < 2 or entropy < 45:
            label = "weak"
        elif len(password) < 14 or variety_score < 3 or entropy < 70:
            label = "medium"
        else:
            label = "strong"

        return {"label": label, "score": score, "entropy": entropy}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def format_timestamp(timestamp: str) -> str:
    return datetime.fromisoformat(timestamp).astimezone().strftime("%Y-%m-%d %H:%M:%S")
