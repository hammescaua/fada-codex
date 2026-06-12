# Arquitetura inicial da FADA

A primeira decisão de arquitetura é começar pelo domínio agrícola mínimo, não por integrações avançadas. Antes de clima, satélite, CAR, IoT, modelos preditivos ou agentes especializados, a plataforma precisa representar bem os fatos básicos da operação rural.

## Princípio de evolução

A evolução será incremental. Cada nova capacidade deve provar que melhora a utilidade do sistema sem destruir simplicidade, robustez ou manutenibilidade.

Para decidir se uma funcionalidade entra agora, usamos quatro perguntas:

1. Por que ela deve ser construída neste momento?
2. Quais pré-requisitos ela exige?
3. Que ganho concreto ela traz para o usuário e para a plataforma?
4. Ela é essencial agora ou deve ficar para uma etapa futura?

## Núcleo do domínio

O núcleo inicial contém quatro conceitos:

- **Propriedade (`Farm`)**: agregado raiz que organiza os dados de uma fazenda.
- **Talhão (`Field`)**: área operacional com nome e tamanho em hectares.
- **Safra (`Season`)**: ciclo produtivo associado a uma cultura e a um período.
- **Operação (`Operation`)**: evento realizado em campo, como plantio, adubação, pulverização ou colheita.

Esses conceitos foram escolhidos porque são fundacionais. Custos, produtividade, documentos, clima, solo, imagens e análises financeiras dependem de um histórico confiável de áreas, safras e operações.

## Persistência

A persistência inicial usa um arquivo JSON local por meio do `JsonFarmRepository`.

Essa escolha é deliberadamente simples:

- reduz dependências externas;
- facilita testes automatizados;
- torna os dados legíveis por humanos;
- permite validar o domínio antes de introduzir banco de dados;
- mantém o projeto fácil de executar em qualquer ambiente.

Quando o produto exigir múltiplos usuários, concorrência, permissões avançadas ou consultas complexas, a troca para um banco relacional será natural. Até lá, o JSON evita complexidade prematura.

## CLI inicial

A CLI `fada` permite executar os primeiros fluxos do produto:

```bash
fada init "Fazenda Modelo"
fada add-field "Talhão Norte" 42.5
fada add-season Soja 2026-09-01
fada summary
```

Ela existe para validar rapidamente o comportamento do domínio sem depender ainda de interface web, autenticação, filas, agentes ou serviços externos.

## O que fica propositalmente fora agora

As seguintes capacidades são importantes, mas ainda são prematuras para a fundação inicial:

- previsão de produtividade;
- análise de risco climático;
- integração com CAR;
- sensoriamento remoto;
- visão computacional;
- IoT e sensores;
- multiagentes especializados;
- simulações financeiras complexas.

Elas dependem de dados confiáveis e histórico operacional. Implementá-las agora aumentaria a complexidade antes de existir uma base sólida para validar resultados.

## Próximos passos recomendados

O próximo passo mais importante é enriquecer o histórico operacional de forma simples:

1. adicionar custos básicos por operação;
2. registrar insumos usados em uma operação;
3. associar produtividade colhida a uma safra e talhão;
4. gerar indicadores simples por hectare.

Essa sequência cria uma ponte natural entre operação de campo e análise econômica, sem exigir IA ou integrações externas no início.
