from typing import Callable, Generic, TypeVar


T = TypeVar("T")


class BufferedStorage(Generic[T]):
    """Data structure to store objects in a buffer and flush them running a callback when the buffer is full."""

    def __init__(
        self, max_size: int, on_buffer_full_callback: Callable[[list[T]], None]
    ):
        self.max_size = max_size
        self.on_buffer_full_callback = on_buffer_full_callback
        self.buffer = []

    async def append(self, signal: T) -> None:
        self.buffer.append(signal)

        if len(self.buffer) >= self.max_size:
            await self.flush()

    async def flush(self) -> int:
        if num_signals := len(self.buffer):
            # Call the callback function with the buffered items
            await self.on_buffer_full_callback(self.buffer)

            # Clear the buffer after flushing
            self.buffer = []

        return num_signals
