class DomainError(Exception):
    """Base for business-rule failures. Translated to HTTP in core/error_handlers.py."""

    code = "DOMAIN_ERROR"
    default_message = "The request could not be completed."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class EmailAlreadyRegisteredError(DomainError):
    code = "EMAIL_ALREADY_REGISTERED"
    default_message = "An account with this email already exists."


class MobileAlreadyRegisteredError(DomainError):
    code = "MOBILE_ALREADY_REGISTERED"
    default_message = "An account with this mobile number already exists."


class BarangayNotFoundError(DomainError):
    code = "BARANGAY_NOT_FOUND"
    default_message = "The selected barangay does not exist."


class InvalidCredentialsError(DomainError):
    code = "INVALID_CREDENTIALS"
    default_message = "Incorrect email or password."


class AuthenticationRequiredError(DomainError):
    code = "AUTHENTICATION_REQUIRED"
    default_message = "Authentication is required."


class InvalidVerificationTokenError(DomainError):
    code = "INVALID_VERIFICATION_TOKEN"
    default_message = "The verification link is invalid or has expired."


class EmailNotVerifiedError(DomainError):
    code = "EMAIL_NOT_VERIFIED"
    default_message = "Verify your email address before submitting a report."


class InvalidRefreshTokenError(DomainError):
    code = "INVALID_REFRESH_TOKEN"
    default_message = "The refresh token is invalid, expired or already used."


class InsufficientRoleError(DomainError):
    code = "FORBIDDEN"
    default_message = "Your role is not allowed to perform this action."
