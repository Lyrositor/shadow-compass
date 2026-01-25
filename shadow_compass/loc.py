from dataclasses import dataclass


@dataclass(frozen=True)
class Loc:
    text: str
    loc_id: str
    fallback: str | None = None
