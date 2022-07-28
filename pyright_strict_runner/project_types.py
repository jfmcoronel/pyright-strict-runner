from dataclasses import dataclass
from enum import Enum, auto
from typing import Sequence, Union


@dataclass(frozen=True)
class CompileSuccess:
    ...


class CompileError(Enum):
    PyrightIgnoreError = auto()
    TypeIgnoreError = auto()
    PyrightTypeError = auto()


CompileResult = Union[CompileSuccess, Sequence[CompileError]]
