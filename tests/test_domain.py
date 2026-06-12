from datetime import date

import pytest

from fada.domain import DomainValidationError, Farm, OperationType, Season


def test_farm_tracks_fields_seasons_operations_and_total_area() -> None:
    farm = Farm(name="Fazenda Modelo")
    field_item = farm.add_field("Talhão Norte", 42.5)
    season = farm.add_season("Soja", date(2026, 9, 1))

    operation = farm.record_operation(
        field_id=field_item.id,
        season_id=season.id,
        operation_type=OperationType.PLANTING,
        happened_on=date(2026, 9, 3),
        description="Plantio inicial com população alvo definida.",
    )

    assert farm.total_area_hectares == 42.5
    assert operation.field_id == field_item.id
    assert operation.season_id == season.id
    assert operation.operation_type is OperationType.PLANTING


def test_farm_round_trip_preserves_core_data() -> None:
    farm = Farm(name="Fazenda Modelo")
    field_item = farm.add_field("Talhão Sul", 18.75)
    season = farm.add_season("Milho", date(2026, 2, 10), date(2026, 7, 20))
    farm.record_operation(
        field_id=field_item.id,
        season_id=season.id,
        operation_type=OperationType.HARVEST,
        happened_on=date(2026, 7, 18),
        description="Colheita do talhão sul.",
    )

    restored = Farm.from_dict(farm.to_dict())

    assert restored.id == farm.id
    assert restored.fields[0].id == field_item.id
    assert restored.seasons[0].ends_on == date(2026, 7, 20)
    assert restored.operations[0].description == "Colheita do talhão sul."


def test_field_area_must_be_positive() -> None:
    farm = Farm(name="Fazenda Modelo")

    with pytest.raises(DomainValidationError, match="area_hectares"):
        farm.add_field("Área inválida", 0)


def test_season_end_cannot_be_before_start() -> None:
    with pytest.raises(DomainValidationError, match="ends_on"):
        Season(crop="Soja", starts_on=date(2026, 9, 1), ends_on=date(2026, 8, 31))


def test_operation_requires_existing_field_and_season() -> None:
    farm = Farm(name="Fazenda Modelo")
    field_item = farm.add_field("Talhão Oeste", 12)
    other_farm = Farm(name="Outra Fazenda")
    other_season = other_farm.add_season("Algodão", date(2026, 1, 1))

    with pytest.raises(DomainValidationError, match="season not found"):
        farm.record_operation(
            field_id=field_item.id,
            season_id=other_season.id,
            operation_type=OperationType.OTHER,
            happened_on=date(2026, 1, 2),
            description="Tentativa inconsistente.",
        )
