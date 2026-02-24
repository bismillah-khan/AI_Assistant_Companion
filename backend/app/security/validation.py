from app.core.errors import AppError
from app.security.prompt_injection import detect_prompt_injection


def validate_user_input(text: str) -> None:
    rule = detect_prompt_injection(text)
    if rule:
        raise AppError("prompt_injection_detected", status_code=400)
