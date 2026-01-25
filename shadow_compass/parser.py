import logging
import re
from dataclasses import is_dataclass, fields
from enum import Enum, IntEnum
from types import NoneType, UnionType, GenericAlias
from typing import Any, TypeVar

from shadow_compass.prop import get_prop_metadata
from shadow_compass.schema.common import CustomSchema
from shadow_compass.schema.condition import Condition, list_conditions
from shadow_compass.schema.effect import Effect, list_effects
from shadow_compass.schema.formula import FormulaElement, parse_formula
from shadow_compass.sudanjson import MultiDict

logger = logging.getLogger(__name__)

T = TypeVar('T')


class UnsupportedPropType(RuntimeError):
    pass


def parse_value(data: Any, type_: type | str | Any, ignore_parse_method: bool = False) -> Any:
    assert isinstance(type_, (type, GenericAlias, UnionType))

    if data is None and type_ == NoneType:
        return None
    elif isinstance(data, (dict, MultiDict)) and is_dataclass(type_):
        if issubclass(type_, CustomSchema) and not ignore_parse_method:
            return type_.parse(data, parse_value)
        else:
            return _parse_entity(data, type_)
    elif isinstance(data, (int, str)) and isinstance(type_, type) and issubclass(type_, Enum):
        return type_(int(data) if issubclass(type_, IntEnum) else data)
    elif isinstance(data, (bool, float, int, str)) and type_ in (bool, float, int, str):
        return type_(data)
    elif isinstance(type_, UnionType):
        args = type_.__args__
        for arg in args:
            try:
                return parse_value(data, arg)
            except UnsupportedPropType:
                pass
    elif isinstance(type_, GenericAlias):
        args = type_.__args__
        if isinstance(data, str):
            if _is_tuple_of(type_, FormulaElement):
                return parse_formula(data)[0]
        elif isinstance(data, list):
            if _is_tuple(type_):
                return tuple(parse_value(d, args[0]) for d in data)
        elif isinstance(data, (dict, MultiDict)):
            if _is_tuple_of(type_, Condition):
                return _parse_conditions(data)
            if _is_tuple_of(type_, Effect):
                return _parse_effects(data)
            if type_.__origin__ is dict and len(args) == 2:
                return {parse_value(k, args[0]): parse_value(v, args[1]) for k, v in data.items()}

    raise UnsupportedPropType(f'Invalid type {type_} for data: {data}')


def _is_tuple_of(tuple_: GenericAlias, of: type) -> bool:
    return _is_tuple(tuple_) and tuple_.__args__[0] is of


def _is_tuple(tuple_: GenericAlias) -> bool:
    return tuple_.__origin__ is tuple and len(tuple_.__args__) == 2 and tuple_.__args__[1] is Ellipsis


def _parse_entity(data: dict[str, Any] | MultiDict[str, Any], entity_cls: Any) -> Any:
    assert is_dataclass(entity_cls) and isinstance(entity_cls, type)

    entity_kwargs = {}
    props = set(data.keys())
    for entity_field in fields(entity_cls):
        metadata = get_prop_metadata(entity_field)
        prop_name = entity_field.name
        if metadata and metadata.name:
            prop_name = metadata.name
        if prop_name in data:
            entity_kwargs[entity_field.name] = (
                metadata.parser(data[prop_name]) if metadata and metadata.parser
                else parse_value(data[prop_name], entity_field.type)
            )
            if metadata and metadata.assert_equals is not None:
                if entity_kwargs[entity_field.name] != metadata.assert_equals:
                    raise ValueError(f'Unexpected value for {entity_field.name}: {entity_kwargs[entity_field.name]}')
            props.remove(prop_name)
    if props:
        raise ValueError(f'Unexpected JSON properties for {entity_cls}: {props}')
    return entity_cls(**entity_kwargs)


def _parse_conditions(data: dict[str, Any] | MultiDict[str, Any]) -> tuple[Condition, ...]:
    return tuple(c for key, value in data.items() if (c := _parse_condition(key, value)))


def _parse_condition(key: str, value: Any) -> Condition | None:
    matches = []
    for (pattern, condition_cls) in list_conditions():
        if match := re.match(rf'^{pattern}$', key):
            matches.append(parse_value({'value': value, **match.groupdict()}, condition_cls))
    if not matches:
        logger.warning(f'Invalid condition {key}: {value}')
        return None
    if len(matches) > 1:
        logger.warning(f'Ambiguous condition {key}, matches: {", ".join(str(m) for m in matches)}')
        return None
    return matches[0]


def _parse_effects(data: dict[str, Any] | MultiDict[str, Any]) -> tuple[Effect, ...]:
    return tuple(e for key, value in data.items() if (e := _parse_effect(key, value)))


def _parse_effect(key: str, value: Any) -> Effect | None:
    matches = []
    for (pattern, effect_cls) in list_effects():
        if match := re.match(rf'^{pattern}$', key):
            matches.append(parse_value({'value': value, **match.groupdict()}, effect_cls))
    if not matches:
        logger.warning(f'Invalid effect {key}: {value}')
        return None
    if len(matches) > 1:
        logger.warning(f'Ambiguous effect key {key}, matches: {", ".join(str(m) for m in matches)}')
        return None
    return matches[0]
