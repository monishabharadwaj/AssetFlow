import re
import secrets
import string

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_MAX_LENGTH = 128

_REQUIREMENTS = (
    (r"[A-Z]", "at least one uppercase letter"),
    (r"[a-z]", "at least one lowercase letter"),
    (r"[0-9]", "at least one number"),
    (r"[^A-Za-z0-9]", "at least one special character"),
)


def validate_password_strength(password: str) -> None:
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {_PASSWORD_MIN_LENGTH} characters")
    if len(password) > _PASSWORD_MAX_LENGTH:
        raise ValueError(f"Password must be at most {_PASSWORD_MAX_LENGTH} characters")

    missing = [desc for pattern, desc in _REQUIREMENTS if not re.search(pattern, password)]
    if missing:
        raise ValueError("Password must contain " + ", ".join(missing))


def generate_temporary_password(length: int = 14) -> str:
    """Generate a unique temporary password that satisfies the policy."""
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*")
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    remaining = [secrets.choice(alphabet) for _ in range(max(length - 4, 0))]
    chars = [upper, lower, digit, special, *remaining]
    secrets.SystemRandom().shuffle(chars)
    password = "".join(chars)
    validate_password_strength(password)
    return password
