"""Persistência local simples para a fase inicial do produto."""

from __future__ import annotations

import json
from pathlib import Path

from fada.domain import Farm


class JsonFarmRepository:
    """Repositório JSON para prototipar fluxos sem banco de dados.

    O objetivo não é substituir um banco relacional no futuro, mas oferecer uma
    fundação reproduzível, fácil de testar e suficiente para validar o domínio.
    """

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def save(self, farm: Farm) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(farm.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        self.path.write_text(payload + "\n", encoding="utf-8")

    def load(self) -> Farm:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return Farm.from_dict(payload)

    def exists(self) -> bool:
        return self.path.exists()
