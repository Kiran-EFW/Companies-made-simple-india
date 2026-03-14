import re


_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
_PHONE_RE = re.compile(r"^(\+91)?[6-9]\d{9}$")
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Verhoeff tables for Aadhaar checksum validation
_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]


def _verhoeff_checksum(number: str) -> bool:
    c = 0
    digits = [int(d) for d in reversed(number)]
    for i, digit in enumerate(digits):
        c = _VERHOEFF_D[c][_VERHOEFF_P[i % 8][digit]]
    return c == 0


def validate_pan(pan: str) -> bool:
    return bool(_PAN_RE.match(pan))


def validate_aadhaar(aadhaar: str) -> bool:
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return False
    return _verhoeff_checksum(aadhaar)


def validate_phone(phone: str) -> bool:
    return bool(_PHONE_RE.match(phone))


def validate_email_format(email: str) -> str:
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise ValueError("Invalid email format")
    return email
