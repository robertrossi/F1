# 🏎️ F1 — volta rápida

### Entre no cockpit e explore as voltas mais rápidas da Fórmula 1.

Um dashboard interativo feito com Streamlit e alimentado pela [API OpenF1](https://openf1.org/). Escolha uma temporada, selecione um circuito e veja o top 5 de voltas válidas em sessões de corrida.

> ☁️ **Quer experimentar sem instalar?** O dashboard ainda não está publicado online. Para publicar, conecte este repositório ao [Streamlit Community Cloud](https://share.streamlit.io/) e use `src/f1/dashboard.py` como arquivo principal. Depois, adicione aqui o link público do app.

## 🎮 Dê uma volta

No dashboard, você pode:

1. Escolher uma temporada a partir de 2023.
2. Selecionar um circuito.
3. Comparar as cinco voltas mais rápidas disponíveis, com piloto, equipe, GP e número da volta.

Os resultados vêm da OpenF1. A primeira consulta pode levar alguns segundos; os dados carregados ficam em cache por seis horas para agilizar visitas seguintes.

## 🚦 Rode na sua máquina

Você precisa do [Python 3.11.5 ou superior](https://www.python.org/downloads/) e do [uv](https://docs.astral.sh/uv/getting-started/installation/).

```powershell
git clone https://github.com/robertrossi/F1.git
cd F1
uv sync --locked
uv run streamlit run src/f1/dashboard.py
```

O Streamlit abrirá a página no navegador. Se isso não acontecer, acesse [http://localhost:8501](http://localhost:8501). O app precisa de conexão com a internet para consultar a API OpenF1.

## 🏁 Como funciona o ranking

- Inclui apenas sessões de corrida (`Race`); treinos, classificação e sprint ficam fora.
- Descarta voltas sem tempo válido e voltas de saída dos boxes.
- Ordena pelo menor tempo e mostra até cinco voltas por circuito e temporada.
- Um piloto pode aparecer mais de uma vez.

## 🧰 Nos bastidores

- `src/f1/api/client.py` cuida das consultas HTTP, filtros e tratamento de erros.
- `src/f1/services/fastest_laps.py` aplica as regras de seleção e classificação das voltas.
- `src/f1/dashboard.py` monta a interface interativa.
- `tests/unit/` contém testes sem chamadas à rede.
- `docs/` reúne a documentação do projeto.

## 🧪 Verificações de desenvolvimento

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mkdocs build --strict
```

Veja a [documentação do projeto](docs/index.md), o [resumo da API](doc_api.md) e os [padrões de engenharia](SKILL.md).
