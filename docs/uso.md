# Uso

## Dashboard

Inicie o app na raiz do projeto:

```bash
uv run streamlit run src/f1/dashboard.py
```

Escolha a temporada e o circuito. O ranking apresenta até cinco voltas por circuito naquela temporada, incluindo piloto, equipe, tempo, GP e número da volta. O cálculo considera somente sessões cujo tipo OpenF1 é `Race`; corridas sprint não entram. Voltas com duração ausente, inválida ou não positiva, e voltas marcadas como saída dos boxes, são descartadas. O mesmo piloto pode ocupar mais de uma posição.

As consultas de voltas são feitas por sessão de corrida e ficam em cache por seis horas. A API cobre dados históricos a partir de 2023. Resultados e campos podem variar conforme a sessão.

## Cliente Python

```python
from f1 import OpenF1Client

with OpenF1Client() as api:
    meetings = api.get_meetings(year=2025, country_name="Brazil")
    sessions = api.get_sessions(meeting_key=1273)
    laps = api.get_laps(session_key=9869, is_pit_out_lap=False)
```

Filtros aceitam parâmetros comuns da API. Operadores como `date>=` devem ser passados como chaves de dicionário; sequências de valores repetem a chave:

```python
laps = api.get(
    "laps",
    session_key=9869,
    driver_number=[1, 44],
    **{"date>=": "2025-03-16T14:00:00Z", "date<=": "2025-03-16T15:00:00Z"},
)
```

Datas são UTC em ISO 8601. Campos opcionais e `null` são preservados. Erros HTTP geram `OpenF1HTTPError`; problemas de rede e timeout geram `OpenF1ConnectionError`; respostas incompatíveis geram `OpenF1Error`. Consulte [`doc_api.md`](doc_api.md) para disponibilidade e limitações. A telemetria e a localização podem retornar grandes volumes e devem ser filtradas por sessão, piloto e/ou período.
