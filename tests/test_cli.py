from fada.cli import main


def test_cli_initializes_farm_and_prints_summary(tmp_path, capsys) -> None:
    data_path = tmp_path / "farm.json"

    assert main(["--data", str(data_path), "init", "Fazenda CLI"]) == 0
    assert main(["--data", str(data_path), "add-field", "Talhão 1", "10.5"]) == 0
    assert main(["--data", str(data_path), "add-season", "Soja", "2026-09-01"]) == 0
    assert main(["--data", str(data_path), "summary"]) == 0

    output = capsys.readouterr().out
    assert "Propriedade: Fazenda CLI" in output
    assert "Área total: 10.50 ha" in output
    assert "Safras: 1" in output
