# OpenF1 API — resumo

Resumo prático da [documentação oficial](https://openf1.org/docs/#api-endpoints). A OpenF1 é uma API não oficial para dados históricos e ao vivo de Fórmula 1.

## Acesso e formato

- **Base URL:** `https://api.openf1.org/v1`
- Os endpoints retornam JSON por padrão; a API também oferece formato CSV.
- Dados históricos a partir de 2023 são gratuitos e não exigem autenticação.
- Dados em tempo real exigem assinatura paga.
- Os exemplos abaixo são requisições HTTP GET. Campos desconhecidos ou sem dados podem vir como `null`.

## Endpoints principais

| Endpoint | O que retorna |
|---|---|
| `/meetings` | Etapas/GPs e testes: circuito, país, local e datas. |
| `/sessions` | Sessões de uma etapa: treinos, classificação, corrida etc. |
| `/drivers` | Pilotos participantes, número, nome, equipe e cor da equipe. |
| `/car_data` | Telemetria do carro (velocidade, RPM, marcha, acelerador, freio e DRS; ~3,7 Hz). |
| `/location` | Coordenadas aproximadas dos carros na pista (~3,7 Hz). |
| `/laps` | Voltas, tempos de setores, velocidades e dados de mini-setores. |
| `/intervals` | Intervalo até o carro à frente e diferença para o líder (corridas; atualização ~4 s). |
| `/position` | Posição dos pilotos ao longo da sessão. |
| `/pit` | Passagens e paradas no pit lane. |
| `/stints` | Stints e compostos de pneus, voltas e idade inicial do pneu. |
| `/race_control` | Mensagens de controle de corrida, bandeiras e eventos. |
| `/session_result` | Resultado final da sessão, posição, tempo e status. |
| `/starting_grid` | Posições de largada. |
| `/weather` | Condições meteorológicas na pista (atualização ~1 min). |
| `/team_radio` | Links para algumas gravações de rádio disponíveis. |
| `/overtakes` | Mudanças de posição em corridas; podem incluir pit stops e penalidades. |
| `/championship_drivers`, `/championship_teams` | Classificação do campeonato (beta; sessões de corrida). |

## Como consultar

Os filtros são enviados na query string. É possível combinar campos:

```text
https://api.openf1.org/v1/drivers?session_key=latest
https://api.openf1.org/v1/meetings?year=2025&country_name=Brazil
https://api.openf1.org/v1/laps?session_key=latest&driver_number=1&lap_number=10
https://api.openf1.org/v1/car_data?session_key=latest&driver_number=1&speed>=300
```

Parâmetros de comparação aceitos:

- Igualdade: `campo=valor`
- Comparações numéricas: `campo>=valor`, `campo<=valor`, `campo>valor`, `campo<valor`
- Intervalo de datas: `date>=...` e `date<=...`
- Para filtrar por mais de um valor do mesmo campo, repita o parâmetro. Exemplo: `driver_number=1&driver_number=44`.

Em URLs montadas manualmente, codifique caracteres especiais da query string quando necessário (por exemplo, `<` como `%3C`).

## Identificadores e datas

- `meeting_key` identifica um fim de semana/etapa; `session_key` identifica uma sessão específica.
- Use `latest` para consultar a etapa ou sessão mais recente, quando o endpoint aceitar esse identificador.
- `driver_number` identifica o piloto naquela temporada.
- Datas são informadas em UTC no formato ISO 8601. Prefira incluir o fuso, por exemplo: `2025-03-16T15:00:00Z`.
- Uma consulta ampla pode retornar muitos registros, especialmente em telemetria e localização; filtre por sessão, piloto e/ou janela de tempo.

## Exemplo com cURL

```bash
curl "https://api.openf1.org/v1/sessions?year=2025&country_name=Brazil"
```

## Observações

- Nem todos os endpoints têm dados para todas as sessões; confira a descrição de cada endpoint na documentação.
- `/laps`: mini-setores não estão disponíveis durante corridas e podem não corresponder exatamente às cores exibidas na transmissão.
- `/overtakes`: disponível apenas em corridas e pode estar incompleto.
- `/session_result` e `/starting_grid` são publicados alguns minutos após os dados oficiais correspondentes.
- `/team_radio` contém apenas uma seleção de comunicações; a disponibilidade caiu bastante a partir de 2026.
- Os endpoints de campeonato estão marcados como beta e são apenas para corridas.
- A OpenF1 é um projeto independente e não é afiliado à Fórmula 1.

## Referência

- [Documentação oficial — API endpoints e filtros](https://openf1.org/docs/#api-endpoints)
