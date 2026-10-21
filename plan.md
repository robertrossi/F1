# Plano do projeto F1

## Objetivo

Criar um dashboard Streamlit que consome a API OpenF1 e exibe, por circuito e temporada, as cinco voltas válidas mais rápidas realizadas em sessões de corrida.

O histórico gratuito da API começa em 2023. O ranking inclui sessões com `session_type=Race`; treinos, classificação e sessões sprint não entram. A interface permite selecionar uma temporada e um circuito. Cada linha mostra posição, tempo, piloto, equipe, GP e número da volta. Um piloto pode aparecer mais de uma vez.

## Regras do ranking

- Agrupar pelo `circuit_key` da etapa; usar o nome curto do circuito como rótulo.
- Buscar sessões da temporada e incluir somente sessões `Race`.
- Buscar voltas por `session_key`, pedindo `is_pit_out_lap=false`.
- Descartar ainda no serviço voltas com duração ausente, inválida, não finita ou não positiva, bem como registros marcados como volta de saída.
- Associar `driver_number` a `drivers` da mesma sessão.
- Ordenar por `lap_duration` crescente e retornar até cinco voltas para o circuito selecionado.
- Manter resultados em cache por seis horas para reduzir consultas repetidas; não persistir dados em banco.

## Arquitetura

- `src/f1/api/client.py`: transporte HTTP, filtros, timeout, erros próprios e repetição limitada para HTTP 429.
- `src/f1/services/fastest_laps.py`: serviço de domínio com gateway injetável, seleção de sessões de corrida e ranking puro.
- `src/f1/dashboard.py`: interface Streamlit, filtros de temporada e circuito, cache e renderização.
- `src/f1/logging_config.py`: logs estruturados JSON Lines.
- `tests/unit/`: testes sem acesso à rede para transporte, regras do ranking, erros e renderização auxiliar.
- `docs/`: instalação, uso e arquitetura.

## Engenharia e qualidade

- Gerenciar dependências e ambiente com uv; manter `uv.lock` sincronizado e usar `uv sync --locked`.
- Usar layout `src/`, type hints, módulos coesos e injeção de dependências.
- Configurar Ruff para lint, formatação e organização de imports.
- Usar Pytest e pytest-cov; exigir pelo menos 50% de cobertura do pacote `f1`.
- Usar MkDocs Material para documentar instalação, execução, filtros e critérios do ranking.
- Manter testes unitários determinísticos e sem chamadas à OpenF1.

## Comandos

```bash
uv sync --locked
uv run streamlit run src/f1/dashboard.py
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run mkdocs build --strict
```

## Limites dos dados

Campos podem faltar ou ser nulos, e nem toda sessão tem dados de volta publicados. A API pode aplicar limites de frequência; o cliente usa repetição limitada para HTTP 429. Telemetria detalhada não é necessária para o ranking inicial. O produto consulta dados históricos, sem autenticação de tempo real.

Referências: [doc_api.md](doc_api.md), [SKILL.md](SKILL.md) e [documentação oficial da OpenF1](https://openf1.org/docs/).
