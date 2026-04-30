# Fluxo de desenvolvimento (Git)

Este documento é um exemplo prático de “padronização do uso do Git” aplicado a este projeto.

## 1) Regras do repositório (recomendadas)

No GitHub (Settings → Branches → Branch protection rules), para `main`:

- Bloquear push direto em `main`
- Exigir Pull Request (PR) para merge
- Exigir 1 aprovação (ou mais)
- Exigir checks passando (CI)
- (Opcional) Exigir branch atualizada antes do merge

## 2) Nomenclatura de branches

- `feature/<slug>`: trabalho novo
- `bugfix/<slug>`: correção
- `hotfix/<slug>`: correção urgente

Slug: curto, em kebab-case, descrevendo o que muda.

## 3) Commits (Conventional Commits)

Por que: facilita leitura do histórico, revisão e automação (changelog/versionamento no futuro).

Padrão:

`tipo(escopo opcional): mensagem`

Exemplos reais para este projeto:
- `feat(ingestion): implementa retry/backoff no client`
- `fix(transform): normaliza UF ausente como null`
- `refactor(database): isola init_db do connection pool`
- `docs: adiciona guia de fluxo Git`

## 4) PRs (checklist)

Todo PR deveria responder:
- Qual o objetivo?
- Qual o impacto (dados, schema, performance, risco)?
- Como testar (comandos e/ou passos)?
- O que foi validado?

## 5) Estrutura e responsabilidades

Heurística útil:
- `app/main.py`: orquestra o fluxo e CLI; evita regras de negócio pesadas.
- `app/ingestion/*`: API e persistência raw.
- `app/transform/*`: normalização/limpeza e contratos de dados.
- `app/load/*`: escrita no banco.
- `app/analytics/*`: KPIs e qualidade.
- `sql/*`: DDL/queries versionadas.
- `docs/*`: documentação viva.

## 6) Automatizações (CI e pre-commit)

Este repo inclui:
- Template de PR em `.github/pull_request_template.md`
- CI simples em `.github/workflows/ci.yml`
- `pre-commit` com `ruff` (lint/format) e checks básicos

Objetivo: impedir que “código ruim” entre em `main` e dar feedback rápido.

