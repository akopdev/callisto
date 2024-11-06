import asyncio
import inspect
from collections import OrderedDict
from functools import partial, wraps
from typing import Callable, Dict, Optional

from .layers import Layers


class Callisto:
    def __init__(self):
        self._tasks: Dict[str, Callable] = OrderedDict()

    def task(self, func: Optional[Callable] = None, *, name: Optional[str] = None) -> Callable:
        if func is None:
            return partial(self.task, name=name)

        @wraps(func)
        async def wrapper() -> None:
            signature = inspect.signature(func)
            if signature.parameters:
                params = {k: self._layers.get(k) for k in signature.parameters.keys()}
                if asyncio.iscoroutinefunction(func):
                    return await func(**params)
                return func(**params)
            if asyncio.iscoroutinefunction(func):
                return await func()
            return func()

        label = name or func.__name__
        self._tasks[label] = wrapper
        return wrapper

    def run(self):
        # Initialise layers from tasks
        self._layers = Layers(self._tasks)
        # Run tasks
        for name, task in self._tasks.items():
            result = self._layers.add(task, name)
        return result
