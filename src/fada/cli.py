"""Interface de linha de comando para operar a fundação inicial."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from uuid import UUID

from fada.domain import Farm, OperationType
from fada.storage import JsonFarmRepository

DEFAULT_DATA_PATH = Path("data/farm.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fada",
        description="CLI inicial da FADA para cadastrar propriedade, talhões, safras e operações.",
    )
    parser.add_argument(
        "--data",
        default=DEFAULT_DATA_PATH,
        type=Path,
        help="Caminho do arquivo JSON local usado como armazenamento.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Cria uma propriedade vazia.")
    init_parser.add_argument("name", help="Nome da propriedade.")

    field_parser = subparsers.add_parser("add-field", help="Adiciona um talhão.")
    field_parser.add_argument("name", help="Nome do talhão.")
    field_parser.add_argument("area_hectares", type=float, help="Área do talhão em hectares.")

    season_parser = subparsers.add_parser("add-season", help="Adiciona uma safra.")
    season_parser.add_argument("crop", help="Cultura da safra, por exemplo soja ou milho.")
    season_parser.add_argument("starts_on", type=date.fromisoformat, help="Data inicial no formato AAAA-MM-DD.")
    season_parser.add_argument("--ends-on", type=date.fromisoformat, help="Data final no formato AAAA-MM-DD.")

    operation_parser = subparsers.add_parser("record-operation", help="Registra uma operação agrícola.")
    operation_parser.add_argument("field_id", type=UUID, help="ID do talhão.")
    operation_parser.add_argument("season_id", type=UUID, help="ID da safra.")
    operation_parser.add_argument("operation_type", choices=[item.value for item in OperationType])
    operation_parser.add_argument("happened_on", type=date.fromisoformat, help="Data da operação no formato AAAA-MM-DD.")
    operation_parser.add_argument("description", help="Descrição objetiva da operação.")

    subparsers.add_parser("summary", help="Exibe um resumo da propriedade.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repository = JsonFarmRepository(args.data)

    if args.command == "init":
        farm = Farm(name=args.name)
        repository.save(farm)
        print(f"Propriedade criada: {farm.name} ({farm.id})")
        return 0

    farm = _load_existing_farm(repository, parser)

    if args.command == "add-field":
        field_item = farm.add_field(args.name, args.area_hectares)
        repository.save(farm)
        print(f"Talhão criado: {field_item.name} ({field_item.id})")
        return 0

    if args.command == "add-season":
        season = farm.add_season(args.crop, args.starts_on, args.ends_on)
        repository.save(farm)
        print(f"Safra criada: {season.crop} ({season.id})")
        return 0

    if args.command == "record-operation":
        operation = farm.record_operation(
            field_id=args.field_id,
            season_id=args.season_id,
            operation_type=OperationType(args.operation_type),
            happened_on=args.happened_on,
            description=args.description,
        )
        repository.save(farm)
        print(f"Operação registrada: {operation.operation_type.value} ({operation.id})")
        return 0

    if args.command == "summary":
        print(_format_summary(farm))
        return 0

    parser.error(f"Comando não suportado: {args.command}")
    return 2


def _load_existing_farm(repository: JsonFarmRepository, parser: argparse.ArgumentParser) -> Farm:
    if not repository.exists():
        parser.error("Nenhuma propriedade encontrada. Execute primeiro: fada init <nome>")
    return repository.load()


def _format_summary(farm: Farm) -> str:
    lines = [
        f"Propriedade: {farm.name}",
        f"ID: {farm.id}",
        f"Área total: {farm.total_area_hectares:.2f} ha",
        f"Talhões: {len(farm.fields)}",
        f"Safras: {len(farm.seasons)}",
        f"Operações: {len(farm.operations)}",
    ]

    if farm.fields:
        lines.append("")
        lines.append("Talhões cadastrados:")
        for field_item in farm.fields:
            lines.append(f"- {field_item.name}: {field_item.area_hectares:.2f} ha ({field_item.id})")

    if farm.seasons:
        lines.append("")
        lines.append("Safras cadastradas:")
        for season in farm.seasons:
            end = season.ends_on.isoformat() if season.ends_on else "em aberto"
            lines.append(f"- {season.crop}: {season.starts_on.isoformat()} até {end} ({season.id})")

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
