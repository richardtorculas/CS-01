import re

_PH_MOBILE = re.compile(r"^(?:\+63|63|0)(9\d{9})$")

PASSWORD_MIN_LENGTH = 8
# Upper bound stops absurdly long inputs from being fed to argon2.
PASSWORD_MAX_LENGTH = 128


def normalize_email(value: str) -> str:
    """Emails are unique case-insensitively, so they are stored lowercase."""
    return value.strip().lower()


def normalize_ph_mobile(value: str) -> str:
    """Accept 09XXXXXXXXX, 639XXXXXXXXX or +639XXXXXXXXX; store +639XXXXXXXXX."""
    compact = re.sub(r"[\s-]", "", value)
    match = _PH_MOBILE.match(compact)
    if match is None:
        raise ValueError("Enter a valid Philippine mobile number, e.g. 09171234567.")
    return f"+63{match.group(1)}"
