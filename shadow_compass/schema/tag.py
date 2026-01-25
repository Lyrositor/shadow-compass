from dataclasses import dataclass

from shadow_compass.loc import Loc
from shadow_compass.schema.enums import TagType


@dataclass(frozen=True)
class Tag:
    id: int
    name: str
    code: str
    type: TagType
    text: str
    resource: str
    can_add: bool
    can_visible: bool
    can_inherit: bool
    can_nagative_and_zero: bool
    tag_sfx: str
    tag_rank: int
    attributes: dict[str, int]
    tips: str  # Unused
    tag_vanishing: int  # Unused
    fail_tag: tuple[str, ...]  # Unused

    @property
    def name_(self) -> Loc:
        return Loc(self.name, f'tag_{self.code}_name', self.code)

    @property
    def text_(self) -> Loc:
        return Loc(self.text, f'tag_{self.code}_text')

    @property
    def prevents_rites_from_grabbing(self) -> bool:
        return self.attributes.get('吸附指定') == 1

    def __repr__(self) -> str:
        return f'<Tag id={self.id} code={self.code}>'
