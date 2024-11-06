import asyncio
import atexit
import hashlib
import inspect
import os
import pickle
from collections import OrderedDict
from dataclasses import dataclass
from logging import getLogger
from typing import Callable, Dict, Generic, TypeVar

from typing_extensions import Optional

log = getLogger(__name__)


T = TypeVar("T")


@dataclass
class Layer:
    id: str
    name: str
    result: T


class Layers(Generic[T]):
    def __init__(self, tasks: Dict[str, Callable]):
        # Get previous state
        storage_name = "results.pkl"
        self._layers: Dict[str, Layer] = self._load(storage_name)
        atexit.register(self._dump, storage_name)
        # Clean expired layers
        self._clean_expired(tasks)

    def _load(self, storage_name: str) -> Dict[str, T]:
        """Load layers from the disk."""
        if os.path.exists(storage_name):
            try:
                with open(storage_name, "rb") as storage:
                    return pickle.load(storage)
            except Exception as e:
                log.error(f"Error loading cached layers. {e}")
        return OrderedDict()

    def _dump(self, storage_name: str):
        """Dump data to the persistent storage."""
        try:
            with open(storage_name, "wb") as storage:
                pickle.dump(self._layers, storage)
        except Exception as e:
            log.error(f"Error save layers to the storage. {e}")

    def _clean_expired(self, tasks: Dict[str, Callable]):
        """
        Remove expired layers.

        Remove layers if the source code of the function has changed. It will also remove layers
        for all functions that run after the updated one, even if there are no direct dependencies.
        This approach is taken because I don't want to build a graph of all dependencies,
        and removing all layers above turns out to be a much cheaper operation.
        """
        to_clean = []
        clean_mode = False
        for name, task in tasks.items():
            if not clean_mode:
                task_id = hashlib.sha256(inspect.getsource(task).encode()).hexdigest()
                existing_layer = self._layers.get(name)
                if existing_layer and task_id != existing_layer.id:
                    clean_mode = True
                    to_clean.append(name)
            else:
                to_clean.append(name)
        if to_clean:
            for name in to_clean:
                del self._layers[name]

    def add(self, task: Callable, name: str) -> T:
        layer = self._layers.get(name)
        if not layer:
            result = asyncio.run(task())
            id = hashlib.sha256(inspect.getsource(task).encode()).hexdigest()
            self._layers[name] = Layer(id=id, name=name, result=result)
            return result
        return layer.result

    def get(self, name: str) -> Optional[T]:
        if layer := self._layers.get(name):
            return layer.result
