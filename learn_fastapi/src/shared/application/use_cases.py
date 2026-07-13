from typing import Protocol, TypeVar

InputT_contra = TypeVar("InputT_contra", contravariant=True)
OutputT_contra = TypeVar("OutputT_contra", contravariant=True)


class AsyncUseCase(Protocol[InputT_contra, OutputT_contra]):
    """Base abstract class for all use cases."""

    async def execute(self, input_t: InputT_contra) -> OutputT_contra:
        """Execute the input and return the result."""
