# Arquitetura

`f1.config.Settings` centraliza URL base e timeout. `f1.api.client.OpenF1Client` implementa o transporte HTTP via httpx e oferece consultas a meetings, sessions, drivers e laps. O transporte pode ser injetado para isolar testes.

`f1.services.fastest_laps.FastestLapService` recebe um gateway por protocolo, identifica somente sessões `Race`, associa voltas aos pilotos e retorna o ranking válido por circuito. A regra de ordenação é pura em relação ao transporte: duração crescente; exclui duração ausente, inválida, não positiva e volta de saída dos boxes.

`f1.dashboard` é a interface Streamlit. Os carregadores usam cache de dados com TTL de seis horas, enquanto o serviço recebe o cliente por injeção de dependências. `f1.logging_config` configura logs JSON Lines com eventos e campos úteis de temporada, circuito e sessão.

Os testes unitários usam um gateway falso; não dependem da rede OpenF1. As chamadas de produção têm timeout e erros próprios de conexão e HTTP.
