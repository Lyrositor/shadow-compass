from typing import TextIO, Any, Generic, TypeVar, Iterable

import jsonc


K = TypeVar('K')
V = TypeVar('V')
D = TypeVar('D')


class MultiDict(Generic[K, V]):
    data: tuple[tuple[K, V], ...]

    def __init__(self, data: Iterable[tuple[K, V]]) -> None:
        self.data = tuple(data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, key: K) -> V:
        for k, v in self.data:
            if k == key:
                return v
        raise KeyError(key)

    def __setitem__(self, key, item) -> None:
        raise NotImplementedError('Cannot set items on a multi-dict')

    def __delitem__(self, key) -> None:
        raise NotImplementedError('Cannot delete items on a multi-dict')

    def __iter__(self) -> Iterable[K]:
        for k, _ in self.data:
            yield k

    def __contains__(self, key) -> bool:
        for k, _ in self.data:
            if k == key:
                return True
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.data}"

    def get(
        self,
        key: K,
        default: D = None,  # type: ignore[invalid-parameter-default]
    ) -> V|D:
        if key in self:
            return self[key]
        return default

    def keys(self) -> Iterable[K]:
        return self.__iter__()

    def items(self) -> Iterable[tuple[K, V]]:
        yield from self.data

    def values(self) -> Iterable[V]:
        for _, value in self.data:
            yield value


def load(f: TextIO, use_multi_dict: bool = True) -> Any:
    return jsonc.loads(f.read().lstrip('\ufeff'), object_pairs_hook=MultiDict if use_multi_dict else None)