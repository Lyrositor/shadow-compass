from abc import ABC, abstractmethod
from typing import Any, Callable, Self

from shadow_compass.sudanjson import MultiDict

ParseFunc = Callable[[Any, type, bool], Any]


class CustomSchema(ABC):
    @classmethod
    @abstractmethod
    def parse(cls, data: dict[str, Any]|MultiDict[str, Any], parse_func: ParseFunc) -> Self | None:
        raise NotImplementedError


CARD_ID = r'(?P<card_id>\d+)'
COMPARATOR = r'(?P<comparator><|<=|>|>=|=|)'
COUNTER_ID = r'(?P<counter_id>\d+)'
RITE_ID = r'(?P<rite_id>\d+)'
OPERATOR = r'(?P<operator>[=+~-])'
SLOT = r's(?P<slot>\d+)'
TAG = r'(?P<tag>(?a:[^\w<=>.|+/*~()-]+\d*))'
TEXT_ID = r'(?P<text_id>[a-zA-Z\d_]+)'
