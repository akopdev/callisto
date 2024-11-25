import asyncio
import atexit
import hashlib
import inspect
import os
import pickle
from collections import OrderedDict
from functools import partial, wraps
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from rich.console import Console
from rich.progress import Progress

T = TypeVar("T")


class Callisto(Generic[T]):
    def __init__(self, name: str = ".callisto.pkl"):
        self._tasks: Dict[str, Callable] = OrderedDict()
        self.console = Console()

        self._layers: Dict[str, str] = {}
        self._artifacts: Dict[str, T] = {}

        self._restore(name)
        atexit.register(self._dump, name)

    def task(self, func: Optional[Callable] = None, *, name: Optional[str] = None) -> Callable:
        if func is None:
            return partial(self.task, name=name)

        @wraps(func)
        async def wrapper() -> None:
            signature = inspect.signature(func)
            if signature.parameters:
                params = {k: self.get_artifact(k) for k in signature.parameters.keys()}
                if asyncio.iscoroutinefunction(func):
                    return await func(**params)
                return func(**params)
            if asyncio.iscoroutinefunction(func):
                return await func()
            return func()

        label = name or func.__name__
        self._tasks[label] = wrapper
        return wrapper

    def _restore(self, storage_name: str) -> bool:
        """Load layers from the disk."""
        if os.path.exists(storage_name):
            try:
                with open(storage_name, "rb") as storage:
                    data = pickle.load(storage)
                    self._artifacts = data.get("artifacts", {})
                    self._layers = data.get("layers", {})
                    return True
            except Exception as e:
                self.console.log(f"Error loading cached layers. {e}")
        return False

    def _dump(self, storage_name: str):
        """Dump data to the persistent storage."""
        try:
            with open(storage_name, "wb") as storage:
                pickle.dump({"layers": self._layers, "artifacts": self._artifacts}, storage)
        except Exception as e:
            self.console.log(f"Error save layers to the storage. {e}")

    def _clean_expired(self, runtime_layers: Dict[str, Any] = {}) -> bool:
        """
        Remove expired layers.

        Remove layers if the source code of the function has changed. It will also remove layers
        for all functions that run after the updated one, even if there are no direct dependencies.
        This approach is taken because I don't want to build a graph of all dependencies,
        and removing all layers above turns out to be a much cheaper operation.
        """
        # Check if any of runtime layers have changed, if so, remove all layers
        if runtime_layers:
            for name, val in runtime_layers.items():
                if artifact := self.get_artifact(name):
                    if val != artifact:
                        return self.remove_all_layers()

        # Remove layers if task changed
        to_clean = set()
        clean_mode = False
        for name, task in self._tasks.items():
            if not clean_mode:
                task_id = self.get_task_id(task)
                layer_id = self.get_layer_id(name)
                if task_id != layer_id:
                    clean_mode = True
                    to_clean.add(name)
            else:
                to_clean.add(name)
        return all([self.remove_layer(name) for name in to_clean if to_clean])

    def remove_all_layers(self) -> bool:
        """Clear all layers and artifacts."""
        self._layers.clear()
        self._artifacts.clear()
        return True

    def remove_layer(self, name: str) -> bool:
        """Remove one layer and all related artifacts."""
        if id := self.get_layer_id(name):
            del self._layers[name]
            del self._artifacts[id]
            return True
        return False

    def add_layer(self, name: str, artifact: T) -> T:
        """Create a new layer from the task."""
        task = self.get_task(name)
        if not task:
            raise ValueError(f"Task {name} not found")
        id = self.get_task_id(task)
        self._layers[name] = id
        self._artifacts[id] = artifact
        return artifact

    def get_layer_id(self, name: str) -> Optional[T]:
        """Get layer id by name."""
        return self._layers.get(name)

    def get_task_id(self, task: Callable) -> str:
        """Create task id from the source code."""
        if not task or not inspect.isfunction(task):
            raise ValueError("Task must be a function")
        return hashlib.sha256(inspect.getsource(task).encode()).hexdigest()

    def get_task(self, name: str) -> Optional[Callable]:
        return self._tasks.get(name)

    def run_task(self, task: Callable, name: str) -> T:
        """Execute task and return artifact."""
        layer_id = self.get_layer_id(name)
        if not layer_id:
            artifact = asyncio.run(task())
            return self.add_layer(name, artifact)
        return self.get_layer_artifact(layer_id)

    def get_layer_artifact(self, id: str) -> Optional[T]:
        """Get artifact by layer id."""
        return self._artifacts.get(id)

    def add_artifact(self, name: str, artifact: T) -> T:
        """Add artifact to the layer."""
        self._layers[name] = name
        self._artifacts[name] = artifact
        return artifact

    def get_artifact(self, name: str) -> Optional[T]:
        """Get artifact by name."""
        if layer_id := self.get_layer_id(name):
            return self.get_layer_artifact(layer_id)

    def run(self, **kwargs):
        # Clean expired layers
        self._clean_expired(kwargs)

        # Define runtime artifacts
        for name, artifact in kwargs.items():
            self.add_artifact(name, artifact)

        # Run tasks
        progress = Progress(auto_refresh=False)
        with progress:
            for name, task in progress.track(self._tasks.items(), description="Total progress"):
                progress.log(
                    f"Starting [bold yellow]{name}[/bold yellow]",
                )
                result = self.run_task(task, name)
                progress.log(f"Task [bold green]{name}[/bold green] is complete")
            return result
