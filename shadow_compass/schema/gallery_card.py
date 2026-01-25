from dataclasses import dataclass

from shadow_compass.schema.enums import CardDisplayType, CardRarity


@dataclass(frozen=True)
class GalleryCardResource:
    pic_res: str
    rare: CardRarity


@dataclass(frozen=True)
class GalleryCardPlotDataItem:
    guid: str
    plot_title: str
    plot_text: str


@dataclass(frozen=True)
class GalleryCardPlot:
    guid: str
    title: str
    data: tuple[GalleryCardPlotDataItem, ...]


@dataclass(frozen=True)
class GalleryCard:
    id: int
    is_show: int
    show_type: CardDisplayType
    sort: int
    resources: tuple[GalleryCardResource, ...]
    plots: tuple[GalleryCardPlot, ...]
