import pytest

from app.core.password_policy import generate_temporary_password, validate_password_strength


def test_accepts_strong_password() -> None:
    validate_password_strength("TempPass123!")


def test_rejects_short_password() -> None:
    with pytest.raises(ValueError, match="at least"):
        validate_password_strength("short")


def test_rejects_missing_uppercase() -> None:
    with pytest.raises(ValueError, match="uppercase"):
        validate_password_strength("lowercase1!")


def test_rejects_missing_special_character() -> None:
    with pytest.raises(ValueError, match="special"):
        validate_password_strength("NoSpecial1")


def test_generated_temporary_password_satisfies_policy() -> None:
    password = generate_temporary_password()
    validate_password_strength(password)
    assert len(password) >= 8
