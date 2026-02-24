import logging
import re

logger = logging.getLogger("security")

_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("system_override", re.compile(r"(ignore|bypass)\s+.*system", re.IGNORECASE)),
    ("role_confusion", re.compile(r"you\s+are\s+now\s+.*(system|developer)", re.IGNORECASE)),
    ("data_exfil", re.compile(r"(exfiltrate|leak|dump).*\b(secrets?|keys?|tokens?)\b", re.IGNORECASE)),
    ("tool_override", re.compile(r"call\s+the\s+tool\s+.*without\s+permission", re.IGNORECASE)),
]


def detect_prompt_injection(text: str) -> str | None:
    for name, pattern in _RULES:
        if pattern.search(text):
            logger.warning("prompt_injection_detected rule=%s", name)
            return name
    return None
