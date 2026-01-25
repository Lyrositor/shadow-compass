from dataclasses import field, MISSING, dataclass, Field
from typing import Any, Callable

METADATA_KEY = '_prop'


@dataclass
class PropMetadata:
    name: str | None
    parser: Callable[[Any], Any] | None = None
    assert_equals: Any | None = None


def prop(
    name: str | None = None,
    parser: Callable[[Any], Any] | None = None,
    assert_equals: Any | None = None,
    default: Any = MISSING,
    default_factory: Any = MISSING,
) -> Any:
    return field(
        default=default,
        default_factory=default_factory,
        metadata={METADATA_KEY: PropMetadata(name=name, parser=parser, assert_equals=assert_equals)},
    )


def get_prop_metadata(f: Field) -> PropMetadata | None:
    return f.metadata.get(METADATA_KEY)
