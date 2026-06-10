from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


class QueueService:
    def __init__(self, max_concurrent: int = 1):
        self.max_concurrent = max(1, int(max_concurrent or 1))
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._user_locks: dict[int, asyncio.Lock] = {}

    def _get_user_lock(self, user_id: int | None) -> asyncio.Lock | None:
        if user_id is None:
            return None
        try:
            key = int(user_id)
        except (TypeError, ValueError):
            return None

        lock = self._user_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._user_locks[key] = lock
        return lock

    async def run(self, job: Callable[[], Awaitable[Any]], user_id: int | None = None):
        if not callable(job):
            raise TypeError("job must be a callable returning an awaitable")

        user_lock = self._get_user_lock(user_id)

        async with self._semaphore:
            if user_lock is None:
                return await job()

            async with user_lock:
                return await job()

    async def submit(self, job: Callable[[], Awaitable[Any]], user_id: int | None = None):
        return await self.run(job, user_id=user_id)
