# FADA Codex

FADA Codex é a fundação incremental de uma plataforma AgTech. O objetivo é construir uma base simples, robusta e evolutiva para registrar propriedades rurais, talhões, safras e operações agrícolas.

A estratégia é evitar complexidade prematura. Antes de adicionar clima, solo, CAR, satélite, IoT, agentes especializados ou modelos preditivos, o sistema precisa dominar os conceitos essenciais do negócio agrícola.

## O que existe agora

- Modelo de domínio com propriedade, talhão, safra e operação.
- Regras básicas de validação para evitar dados inválidos.
- Persistência local em JSON para prototipagem reprodutível.
- CLI inicial para criar uma propriedade e registrar dados operacionais.
- Testes automatizados para proteger a fundação.
- Documentação de arquitetura e evolução incremental.

## Instalação para desenvolvimento

Requisitos:

- Python 3.11 ou superior.

Crie um ambiente virtual e instale o projeto em modo editável:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e . pytest
```

## Uso da CLI

Crie uma propriedade:

```bash
fada init "Fazenda Modelo"
```

Adicione um talhão:

```bash
fada add-field "Talhão Norte" 42.5
```

Adicione uma safra:

```bash
fada add-season Soja 2026-09-01
```

Consulte o resumo:

```bash
fada summary
```

Por padrão, a CLI grava os dados em `data/farm.json`. Para usar outro arquivo, informe `--data`:

```bash
fada --data /tmp/farm.json init "Fazenda Teste"
```

## Como funciona

O sistema começa com quatro entidades principais:

1. `Farm`: representa a propriedade e funciona como agregado raiz.
2. `Field`: representa um talhão com nome e área em hectares.
3. `Season`: representa uma safra ou ciclo produtivo.
4. `Operation`: representa uma atividade realizada em campo.

A propriedade controla a consistência entre essas entidades. Uma operação só pode ser registrada se o talhão e a safra existirem dentro da própria propriedade.

## Rodando os testes

```bash
python -m pytest
```

## Estratégia de evolução

A plataforma deve crescer por fundações, não por empilhamento de funcionalidades isoladas.

A próxima evolução recomendada é adicionar custos e insumos por operação, porque isso aproveita o histórico operacional recém-criado e abre caminho para indicadores por hectare, análise financeira e estimativas de produtividade.

Leia mais em [`docs/architecture.md`](docs/architecture.md).
