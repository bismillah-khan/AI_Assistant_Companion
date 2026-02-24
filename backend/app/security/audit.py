import logging

logger = logging.getLogger("security")


def log_tool_block(reason: str, tool_name: str, role: str) -> None:
    logger.warning("tool_blocked reason=%s tool=%s role=%s", reason, tool_name, role)


def log_tool_allowed(tool_name: str, role: str) -> None:
    logger.info("tool_allowed tool=%s role=%s", tool_name, role)
