from datetime import date

from fada.domain import Farm
from fada.storage import JsonFarmRepository


def test_json_repository_saves_and_loads_farm(tmp_path) -> None:
    repository = JsonFarmRepository(tmp_path / "farm.json")
    farm = Farm(name="Fazenda Persistida")
    farm.add_field("Talhão Central", 33.3)
    farm.add_season("Café", date(2026, 4, 1))

    repository.save(farm)
    restored = repository.load()

    assert repository.exists()
    assert restored.name == "Fazenda Persistida"
    assert restored.fields[0].name == "Talhão Central"
    assert restored.seasons[0].crop == "Café"
