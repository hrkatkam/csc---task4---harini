from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")



def mux2(select: bool, when_false: T, when_true: T) -> T:
    return when_true if select else when_false
