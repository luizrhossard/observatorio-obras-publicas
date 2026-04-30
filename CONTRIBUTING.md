# Contribuindo

Este repositório usa um fluxo simples e padronizado para facilitar manutenção, revisão e evolução do pipeline.

## Fluxo de branches

- `main`: sempre estável (nada de commit direto).
- `feature/<slug>`: novas funcionalidades (ex.: `feature/etl-retry-backoff`).
- `bugfix/<slug>`: correções não urgentes (ex.: `bugfix/normalize-municipio-id`).
- `hotfix/<slug>`: correções urgentes para `main` (ex.: `hotfix/fix-db-connection-timeout`).

Recomendação (GitHub): proteger a branch `main` e exigir PR + checks.

## Commits (Conventional Commits)

Formato:

`<tipo>(<escopo opcional>): <mensagem curta>`

Tipos comuns:
- `feat`: nova funcionalidade
- `fix`: correção de bug
- `refactor`: refatoração sem mudança de comportamento
- `docs`: documentação
- `test`: testes
- `chore`: manutenção/infra

Exemplos:
- `feat(ingestion): adiciona retry com backoff`
- `fix(load): corrige tipo de coluna localidade_id`
- `docs: documenta fluxo de desenvolvimento`

## Pull Requests

- Abra PR para `main` a partir de `feature/*`, `bugfix/*` ou `hotfix/*`.
- Preencha o template (objetivo, impacto, como testar).
- Preferir PRs pequenos e focados.

## Qualidade mínima (local)

Se você usa Python localmente, recomenda-se:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
pytest
```

