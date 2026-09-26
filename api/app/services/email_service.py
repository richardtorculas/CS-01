import logging
import uuid
from typing import Protocol

import httpx

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


class EmailSender(Protocol):
    def send(self, *, to_email: str, to_name: str, subject: str, text: str) -> None: ...


class BrevoEmailSender:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, *, to_email: str, to_name: str, subject: str, text: str) -> None:
        payload = {
            "sender": {
                "name": self._settings.email_from_name,
                "email": self._settings.email_from_address,
            },
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "textContent": text,
        }
        response = httpx.post(
            BREVO_SEND_URL,
            json=payload,
            headers={"api-key": self._settings.brevo_api_key},
            timeout=10,
        )
        response.raise_for_status()


class DisabledEmailSender:
    """Used when no provider is configured. Deliberately silent: the token is a credential."""

    def send(self, *, to_email: str, to_name: str, subject: str, text: str) -> None:
        logger.info("Email provider not configured; message not sent.")


def get_email_sender() -> EmailSender:
    settings = get_settings()
    if settings.brevo_api_key:
        return BrevoEmailSender(settings)
    return DisabledEmailSender()


def send_verification_email(
    sender: EmailSender, *, user_id: uuid.UUID, to_email: str, to_name: str, token: str
) -> None:
    """Best effort: a delivery failure must not fail registration; the user can request a resend."""
    link = f"{get_settings().verification_link_base}?token={token}"
    text = (
        f"Hello {to_name},\n\n"
        f"Confirm your email address to start submitting reports on UGNAY:\n{link}\n\n"
        "If you did not create this account, you can ignore this message."
    )
    try:
        sender.send(
            to_email=to_email, to_name=to_name, subject="Verify your UGNAY email", text=text
        )
    except Exception as error:
        # Log the id and error type only: exception text or the address could be personal data.
        logger.warning(
            "Verification email delivery failed for user %s (%s).", user_id, type(error).__name__
        )
