from enum import Enum, IntEnum


class CardType(Enum):
    CHAR = 'char'
    ITEM = 'item'
    SULTAN_CARD = 'sudan'

    @property
    def label(self) -> str:
        match self:
            case CardType.CHAR:
                return 'Character'
            case CardType.ITEM:
                return 'Item'
            case CardType.SULTAN_CARD:
                return 'Sultan Card'


class CardDisplayType(Enum):
    ANIMAL = 'animal'
    ARMY = 'army'
    BOOK = 'book'
    CHAR = 'char'
    CONSUMABLES = 'consumables'
    FOOD = 'food'
    NONHUMAN = 'nonhuman'
    OTHER_CHAR = 'other_char'
    OTHERS = 'others'
    TREASURE = 'treasure'
    SUDAN_CARD = 'sudancard'
    SYMBOLISM = 'symbolism'
    WEAPON_EQUIP = 'weapon_equip'

    @property
    def label(self) -> str:
        match self:
            case CardDisplayType.ANIMAL:
                return 'Animal'
            case CardDisplayType.ARMY:
                return 'Army'
            case CardDisplayType.BOOK:
                return 'Book'
            case CardDisplayType.CHAR:
                return 'Main Characters'
            case CardDisplayType.CONSUMABLES:
                return 'Consumable'
            case CardDisplayType.FOOD:
                return 'Food'
            case CardDisplayType.NONHUMAN:
                return 'Nonhuman'
            case CardDisplayType.OTHER_CHAR:
                return 'Secondary Characters'
            case CardDisplayType.OTHERS:
                return 'Others'
            case CardDisplayType.SUDAN_CARD:
                return 'Sultan Card'
            case CardDisplayType.SYMBOLISM:
                return 'Symbolism'
            case CardDisplayType.TREASURE:
                return 'Crowdfund Treasures'
            case CardDisplayType.WEAPON_EQUIP:
                return 'Equipment'


class CardRarity(IntEnum):
    STONE = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4
    SPECIAL = 5

    @property
    def label(self) -> str:
        match self:
            case CardRarity.STONE:
                return 'Stone'
            case CardRarity.BRONZE:
                return 'Bronze'
            case CardRarity.SILVER:
                return 'Silver'
            case CardRarity.GOLD:
                return 'Gold'
            case CardRarity.SPECIAL:
                return 'Beyond Gold'


class Comparator(Enum):
    EQ = '='
    LT = '<'
    LTE = '<='
    GT = '>'
    GTE = '>='

    @property
    def label(self) -> str:
        match self:
            case Comparator.EQ:
                return '='
            case Comparator.LT:
                return '<'
            case Comparator.LTE:
                return '≤'
            case Comparator.GT:
                return '>'
            case Comparator.GTE:
                return '≥'


class Operator(Enum):
    ADD = '+'
    SUB = '-'
    SUB_ALT = '~'
    ASSIGN = '='

    @property
    def label(self) -> str:
        match self:
            case Operator.ADD:
                return 'Add'
            case Operator.SUB:
                return 'Remove'
            case Operator.SUB_ALT:
                return 'Remove'
            case Operator.ASSIGN:
                return 'Assign'


class LootItemType(Enum):
    CARD = 'card'
    EVENT = 'event'
    LOOT = 'loot'
    RITE = 'rite'


class LootType(Enum):
    REGULAR = 2
    NEW_ONLY = 3
    # TODO Figure this out
    UNKNOWN = 4
    ALL = 99

    @property
    def label(self) -> str:
        match self:
            case LootType.REGULAR:
                return 'Regular'
            case LootType.NEW_ONLY:
                return 'New Only'
            case LootType.UNKNOWN:
                return 'Unknown'
            case LootType.ALL:
                return 'All Items'


class RiteResult(Enum):
    CHAR = 'char'
    FIGHT_RESULT = 'fight_result'
    ITEM = 'item'
    NORMAL_RESULT = 'normal_result'
    SUDAN = 'sudan'

    @property
    def label(self) -> str:
        match self:
            case RiteResult.CHAR:
                return 'Character'
            case RiteResult.FIGHT_RESULT:
                return 'Fight Result'
            case RiteResult.ITEM:
                return 'Item'
            case RiteResult.NORMAL_RESULT:
                return 'Normal Result'
            case RiteResult.SUDAN:
                return 'Sultan Card'


class RiteType(Enum):
    ENEMY = 'ENEMY'
    END = 'END'
    TREASURE = 'TREASURE'

    @property
    def label(self) -> str:
        match self:
            case RiteType.ENEMY:
                return 'Enemy'
            case RiteType.END:
                return 'End'
            case RiteType.TREASURE:
                return 'Treasure'


class Slot(Enum):
    ACCESSORY = 'accessory'
    ANIMAL_HANDLING = 'animal_handling'
    CLOTH = 'cloth'
    WEAPON = 'weapon'

    @property
    def label(self) -> str:
        match self:
            case Slot.ACCESSORY:
                return 'Accessory'
            case Slot.ANIMAL_HANDLING:
                return 'Animal Handling'
            case Slot.CLOTH:
                return 'Attire'
            case Slot.WEAPON:
                return 'Weapon'


class TagType(Enum):
    ATTRIBUTE = 'attribute'
    BUFF = 'buff'
    DEBUFF = 'debuff'

    @property
    def label(self) -> str:
        match self:
            case TagType.ATTRIBUTE:
                return 'Attribute'
            case TagType.BUFF:
                return 'Buff'
            case TagType.DEBUFF:
                return 'Debuff'

