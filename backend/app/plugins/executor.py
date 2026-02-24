import importlib.util
import logging
import multiprocessing
from pathlib import Path
from typing import Any

from app.core.errors import AppError

logger = logging.getLogger(__name__)


def execute_tool(entry_path: Path, tool_name: str, args: dict[str, Any], timeout: float) -> Any:
    ctx = multiprocessing.get_context("spawn")
    queue: multiprocessing.Queue = ctx.Queue()
    process = ctx.Process(target=_worker, args=(str(entry_path), tool_name, args, queue))
    process.start()
    process.join(timeout=timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        raise AppError("plugin_timeout", status_code=504)

    if queue.empty():
        raise AppError("plugin_no_response", status_code=502)

    status, payload = queue.get()
    if status == "ok":
        return payload
    raise AppError(str(payload), status_code=502)


def _worker(entry_path: str, tool_name: str, args: dict[str, Any], queue: multiprocessing.Queue) -> None:
    try:
        spec = importlib.util.spec_from_file_location("plugin_entry", entry_path)
        if spec is None or spec.loader is None:
            queue.put(("error", "plugin_entry_not_found"))
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "invoke"):
            queue.put(("error", "plugin_missing_invoke"))
            return

        invoke = getattr(module, "invoke")
        result = invoke(tool_name, args)
        queue.put(("ok", result))
    except Exception as exc:
        logger.exception("plugin_exec_failed")
        queue.put(("error", f"plugin_exec_failed:{exc}"))
