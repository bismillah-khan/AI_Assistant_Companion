import time
from dataclasses import dataclass
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config.settings import get_settings


@dataclass
class _RateState:
    window: int
    count: int


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, time_func: Callable[[], float] | None = None) -> None:
        super().__init__(app)
        self._time_func = time_func or time.time
        self._settings = get_settings()
        self._rate: dict[str, _RateState] = {}

    async def dispatch(self, request: Request, call_next):
        role = request.headers.get("x-client-role") or "user"
        if role not in self._settings.security_allowed_roles:
            return JSONResponse(status_code=403, content={"error": "role_not_allowed"})
        request.state.role = role

        if not self._check_rate_limit(request):
            return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded"})

        return await call_next(request)

    def _check_rate_limit(self, request: Request) -> bool:
        if self._settings.rate_limit_per_minute <= 0:
            return True

        client_ip = request.client.host if request.client else "unknown"
        current_window = int(self._time_func() // 60)
        state = self._rate.get(client_ip)
        if state is None or state.window != current_window:
            self._rate[client_ip] = _RateState(window=current_window, count=1)
            return True

        if state.count >= self._settings.rate_limit_per_minute:
            return False

        state.count += 1
        return True
