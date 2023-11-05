from enum import Enum
from typing import Type, TypeVar, Generic

T = TypeVar("T", bound="BaseEnumGeneric")


class BaseEnum(Enum, Generic[T]):
    @classmethod
    def from_string(cls: Type[T], str_value: str) -> T:
        for member in cls:
            if member.value == str_value:
                return member
        raise ValueError(
            f"Invalid value: {str_value}. Cannot convert to {cls.__name__} enum."
        )
