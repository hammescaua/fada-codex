"""Modelos centrais do domínio agrícola.

Este módulo concentra as entidades mais estáveis do sistema. A escolha inicial é
intencionalmente pequena: propriedade, talhão, safra e operação. Esses conceitos
servem como base para funcionalidades futuras como custos, clima, solo,
produtividade, sensoriamento remoto e análise financeira.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class DomainValidationError(ValueError):
    """Erro levantado quando uma regra simples de domínio é violada."""


class OperationType(StrEnum):
    """Tipos iniciais de operação agrícola.

    A lista começa pequena para evitar acoplamento prematuro. Novos tipos podem
    ser adicionados quando houver necessidade real de produto.
    """

    PLANTING = "planting"
    FERTILIZATION = "fertilization"
    SPRAYING = "spraying"
    HARVEST = "harvest"
    OTHER = "other"


@dataclass(slots=True)
class Field:
    """Talhão ou área operacional dentro de uma propriedade."""

    name: str
    area_hectares: float
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = _require_text(self.name, "field.name")
        if self.area_hectares <= 0:
            raise DomainValidationError("field.area_hectares must be greater than zero")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "area_hectares": self.area_hectares,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Field:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            area_hectares=float(data["area_hectares"]),
        )


@dataclass(slots=True)
class Season:
    """Safra vinculada a uma cultura e a um intervalo de datas."""

    crop: str
    starts_on: date
    ends_on: date | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.crop = _require_text(self.crop, "season.crop")
        if self.ends_on is not None and self.ends_on < self.starts_on:
            raise DomainValidationError("season.ends_on cannot be before season.starts_on")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "crop": self.crop,
            "starts_on": self.starts_on.isoformat(),
            "ends_on": self.ends_on.isoformat() if self.ends_on else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Season:
        return cls(
            id=UUID(data["id"]),
            crop=data["crop"],
            starts_on=date.fromisoformat(data["starts_on"]),
            ends_on=date.fromisoformat(data["ends_on"]) if data.get("ends_on") else None,
        )


@dataclass(slots=True)
class Operation:
    """Registro simples de uma operação feita em campo."""

    field_id: UUID
    season_id: UUID
    operation_type: OperationType
    happened_on: date
    description: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self.description = _require_text(self.description, "operation.description")
        if not isinstance(self.operation_type, OperationType):
            self.operation_type = OperationType(self.operation_type)
        if self.created_at.tzinfo is None:
            raise DomainValidationError("operation.created_at must be timezone-aware")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "field_id": str(self.field_id),
            "season_id": str(self.season_id),
            "operation_type": self.operation_type.value,
            "happened_on": self.happened_on.isoformat(),
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Operation:
        return cls(
            id=UUID(data["id"]),
            field_id=UUID(data["field_id"]),
            season_id=UUID(data["season_id"]),
            operation_type=OperationType(data["operation_type"]),
            happened_on=date.fromisoformat(data["happened_on"]),
            description=data["description"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass(slots=True)
class Farm:
    """Agregado raiz inicial da plataforma.

    A propriedade contém os cadastros e eventos mínimos para construir histórico.
    Regras que dependem de múltiplas entidades ficam aqui para preservar
    consistência antes de persistir os dados.
    """

    name: str
    id: UUID = field(default_factory=uuid4)
    fields: list[Field] = field(default_factory=list)
    seasons: list[Season] = field(default_factory=list)
    operations: list[Operation] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = _require_text(self.name, "farm.name")

    def add_field(self, name: str, area_hectares: float) -> Field:
        field_item = Field(name=name, area_hectares=area_hectares)
        self.fields.append(field_item)
        return field_item

    def add_season(self, crop: str, starts_on: date, ends_on: date | None = None) -> Season:
        season = Season(crop=crop, starts_on=starts_on, ends_on=ends_on)
        self.seasons.append(season)
        return season

    def record_operation(
        self,
        *,
        field_id: UUID,
        season_id: UUID,
        operation_type: OperationType,
        happened_on: date,
        description: str,
    ) -> Operation:
        if not any(field_item.id == field_id for field_item in self.fields):
            raise DomainValidationError(f"field not found: {field_id}")
        if not any(season.id == season_id for season in self.seasons):
            raise DomainValidationError(f"season not found: {season_id}")

        operation = Operation(
            field_id=field_id,
            season_id=season_id,
            operation_type=operation_type,
            happened_on=happened_on,
            description=description,
        )
        self.operations.append(operation)
        return operation

    @property
    def total_area_hectares(self) -> float:
        return sum(field_item.area_hectares for field_item in self.fields)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "fields": [field_item.to_dict() for field_item in self.fields],
            "seasons": [season.to_dict() for season in self.seasons],
            "operations": [operation.to_dict() for operation in self.operations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Farm:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            fields=[Field.from_dict(item) for item in data.get("fields", [])],
            seasons=[Season.from_dict(item) for item in data.get("seasons", [])],
            operations=[Operation.from_dict(item) for item in data.get("operations", [])],
        )


def _require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise DomainValidationError(f"{field_name} cannot be empty")
    return cleaned
