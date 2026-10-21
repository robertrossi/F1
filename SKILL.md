# Padrões de Engenharia Python para Engenharia de Dados

## Sumário

- [Objetivo e escopo](#objetivo-e-escopo)
- [1. Gerenciamento do projeto e ambiente](#1-gerenciamento-do-projeto-e-ambiente)
- [2. Arquitetura e organização](#2-arquitetura-e-organização)
- [3. Padrões de código Python](#3-padrões-de-código-python)
- [4. Lint, formatação e imports com Ruff](#4-lint-formatação-e-imports-com-ruff)
- [5. Testes com Pytest e cobertura](#5-testes-com-pytest-e-cobertura)
- [6. Documentação com MkDocs Material](#6-documentação-com-mkdocs-material)
- [7. Boas práticas de Engenharia de Dados](#7-boas-práticas-de-engenharia-de-dados)
- [8. Git, revisão e CI/CD](#8-git-revisão-e-cicd)
- [9. Fluxo de trabalho do agente de IA](#9-fluxo-de-trabalho-do-agente-de-ia)
- [10. Critério de aplicação](#10-critério-de-aplicação)

## Objetivo e escopo

Este guia orienta agentes de IA e colaboradores na criação, manutenção, revisão e evolução de projetos Python de Engenharia de Dados. Aplique as regras obrigatórias abaixo. Use as recomendações conforme a necessidade e a complexidade do projeto, sem introduzir camadas, ferramentas ou dependências sem justificativa.

## 1. Gerenciamento do projeto e ambiente

### Regras obrigatórias

- Use **uv** para gerenciar o projeto, dependências, ambiente virtual e execução de comandos. Não use `pip` diretamente para instalar, remover ou atualizar pacotes.
- Declare dependências no `pyproject.toml` e mantenha `uv.lock` versionado. Não edite o lockfile manualmente; atualize-o com os comandos do uv.
- Use o ambiente `.venv` gerenciado pelo uv. Não instale globalmente dependências que pertencem ao projeto.
- Registre a versão do Python suportada em `pyproject.toml` e, quando adequado, em `.python-version`.
- Prefira instalações reproduzíveis, inclusive em CI/CD. Use `uv sync --locked` em automações que devem respeitar o lockfile existente.

### Comandos comuns

```bash
uv init
uv add nome-do-pacote
uv add --dev nome-da-ferramenta
uv remove nome-do-pacote
uv sync
uv run python -m pacote
```

Consulte `uv --help` ou a documentação oficial do uv se um comando ou opção não for conhecido. Não invente sintaxe.

## 2. Arquitetura e organização

Adote a estrutura `src/` como padrão. Mantenha o código de produção em `src/projeto/` (substitua `projeto` pelo nome importável do pacote) e adapte a estrutura à escala real do sistema.

```text
projeto/
├── pyproject.toml
├── uv.lock
├── .python-version
├── README.md
├── mkdocs.yml
├── src/
│   └── projeto/
│       ├── __init__.py
│       ├── config.py
│       ├── domain/
│       ├── services/
│       ├── repositories/
│       └── utils/
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    └── index.md
```

As pastas `domain/`, `services/`, `repositories/`, `unit/` e `integration/` são exemplos, não requisitos para projetos pequenos.

### Regras obrigatórias

- Separe código de produção, testes, documentação, configuração e orquestração conforme as responsabilidades do projeto.
- Mantenha módulos coesos, com dependências claras; evite ciclos de importação, módulos monolíticos e abstrações prematuras.
- Separe regras de negócio de I/O e detalhes de infraestrutura quando isso tornar o código mais compreensível e testável.
- Use nomes claros e imports consistentes. Não concentre lógica de produção em notebooks ou scripts monolíticos.
- Use notebooks para exploração e análise; quando apropriado, reutilize neles os módulos do pacote de produção.

## 3. Padrões de código Python

- Siga as convenções PEP 8; use type hints nas interfaces públicas e em outros pontos onde melhorem a clareza.
- Escreva docstrings claras para módulos, classes e funções públicas quando seu propósito ou contrato não for evidente.
- Prefira funções pequenas, coesas e testáveis. Evite efeitos colaterais inesperados e estado mutável compartilhado.
- Trate exceções explicitamente. Não capture exceções genéricas sem uma razão concreta e sem preservar a capacidade de diagnosticar a falha.
- Não use `print()` para logging em produção. Use `logging` ou a solução já adotada pelo projeto.
- Centralize configurações. Não deixe valores específicos de ambiente ou segredos hardcoded no código.
- Nunca versione credenciais, tokens, senhas ou arquivos `.env` que contenham segredos. Use variáveis de ambiente ou um mecanismo apropriado de gestão de segredos.
- Prefira `pathlib` para caminhos e context managers para recursos que precisem ser fechados ou liberados.
- Valide entradas e trate dados ausentes, tipos incorretos e estados inesperados de acordo com o contrato do sistema.

## 4. Lint, formatação e imports com Ruff

Use **Ruff** como ferramenta padrão para lint, formatação e organização de imports. Mantenha a configuração no `pyproject.toml`, com regras adequadas ao projeto. Amplie a seleção de regras de forma gradual e justificada.

```bash
uv add --dev ruff
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .
uv run ruff format --check .
```

- Use `ruff check` para identificar problemas e `ruff check --fix` para correções automáticas suportadas.
- Use `ruff format` para formatar e `ruff format --check` para verificar sem alterar arquivos.
- Ruff também organiza imports por meio das regras correspondentes de lint (por exemplo, `I`), habilitadas na configuração.
- Revise correções automáticas antes de concluir. Não aplique mudanças que possam alterar lógica sem avaliar o impacto.
- Não ignore uma regra globalmente ou em um trecho sem justificativa técnica clara. Prefira exceções locais e documentadas quando necessárias.

## 5. Testes com Pytest e cobertura

Use **Pytest** para testes automatizados e **pytest-cov** para medir cobertura. A cobertura mínima exigida é **50% do código de produção**.

```bash
uv add --dev pytest pytest-cov
uv run pytest
uv run pytest --cov=projeto --cov-report=term-missing --cov-fail-under=50
```

Configure o alvo de cobertura para o pacote correto do projeto. A medição não deve ser inflada por testes, configurações ou arquivos sem relevância. Considere centralizar as opções estáveis em `pyproject.toml` para que a execução local e a CI usem os mesmos critérios.

### Regras de teste

- Mantenha os testes em `tests/`, separados do código de produção. Separe unitários e integração quando isso melhorar a organização.
- Priorize testes unitários de regras de negócio, transformações, validações e comportamentos críticos.
- Cubra caminhos normais, limites, entradas inválidas, valores ausentes e exceções relevantes.
- Isole APIs, bancos, serviços externos, arquivos e outros recursos quando apropriado. Use fixtures, mocks e stubs com critério, sem mascarar o comportamento que precisa ser validado.
- Mantenha testes determinísticos e independentes da ordem de execução, de dados externos instáveis e de configurações pessoais.
- Avalie se os testes verificam o comportamento esperado; a mera existência ou execução de testes não comprova qualidade.
- Não reduza o limite de 50% para contornar falhas. Investigue código sem cobertura e acrescente testes relevantes. Justifique exclusões pontuais de cobertura.

## 6. Documentação com MkDocs Material

Use **MkDocs Material** para a documentação técnica. Mantenha as páginas em `docs/` e a configuração do site em `mkdocs.yml`.

```bash
uv add --dev mkdocs-material
uv run mkdocs serve
uv run mkdocs build --strict
```

Documente objetivo e escopo, instalação, configuração, execução, testes, arquitetura, módulos principais e operação dos pipelines. Explique contratos, entradas, saídas e comportamentos relevantes das interfaces públicas. Inclua exemplos práticos quando ajudarem o leitor.

Mantenha a documentação alinhada ao comportamento atual do código; evite conteúdo redundante ou desatualizado. Use exemplos sem credenciais reais. Valide a compilação com `mkdocs build --strict` quando a documentação ou sua configuração mudar.

## 7. Boas práticas de Engenharia de Dados

- Separe extração, validação, transformação, carregamento e orquestração quando essa divisão ajudar a manter responsabilidades claras.
- Prefira transformações reproduzíveis e idempotentes. Defina contratos de dados e valide schemas, tipos, campos obrigatórios e restrições relevantes.
- Trate duplicidades, valores ausentes, registros inválidos e mudanças inesperadas de schema de forma explícita.
- Evite carregar grandes volumes integralmente na memória sem necessidade. Considere uso de memória, custo computacional, filtros, processamento incremental e particionamento conforme o caso.
- Prefira operações vetorizadas ou recursos nativos da plataforma de processamento quando forem adequados e legíveis.
- Separe regras de negócio de detalhes de infraestrutura. Gerencie conexões, transações, timeouts e retries com critérios claros e limites definidos.
- Registre contexto útil para rastreabilidade, diagnóstico e auditoria. Não inclua credenciais, dados pessoais ou informações sensíveis nos logs.
- Faça falhas ficarem identificáveis; não permita que uma execução incompleta aparente sucesso.
- Separe configurações por ambiente e considere recuperação de falhas parciais quando aplicável.
- Não imponha ferramenta, arquitetura ou dependência específica sem necessidade demonstrada pelo projeto.

## 8. Git, revisão e CI/CD

- Versione código, testes, documentação, `pyproject.toml` e `uv.lock`.
- Ignore `.venv`, caches, arquivos temporários, segredos, dados locais e artefatos gerados usando `.gitignore`.
- Faça alterações pequenas, coesas e fáceis de revisar. Siga a convenção de mensagens de commit do repositório; se ela não existir, mantenha um padrão consistente.
- Não altere arquivos ou funcionalidades fora do escopo sem necessidade justificada.
- Revise com atenção mudanças em dependências, lockfile, schemas e contratos de dados.
- Recomende CI que sincronize dependências de forma reproduzível e execute as verificações relevantes automaticamente.
- Antes de concluir uma mudança, execute as verificações pertinentes: lint, formatação, testes com cobertura e compilação da documentação quando aplicável. Informe verificações que não puderam ser executadas e o motivo; não declare sucesso sem evidência.

## 9. Fluxo de trabalho do agente de IA

Ao trabalhar em um projeto Python de Engenharia de Dados:

1. Inspecione a estrutura, as instruções locais e as configurações existentes antes de editar.
2. Respeite os padrões já adotados e evite introduzir ferramentas redundantes.
3. Considere modularidade, testabilidade e impacto em interfaces e contratos de dados.
4. Implemente a menor solução que atenda aos requisitos sem sacrificar clareza ou qualidade.
5. Crie ou atualize testes para o comportamento alterado e atualize a documentação quando necessário.
6. Execute Ruff, Pytest com o limite de cobertura e validação MkDocs conforme aplicável; corrija falhas e repita as verificações.
7. Nunca afirme ter executado comandos ou testes que não executou.
8. Ao relatar a conclusão, informe arquivos alterados, comandos executados e resultados. Declare limitações ou verificações pendentes com clareza.
9. Peça esclarecimento quando faltar um requisito essencial ou uma regra de negócio não puder ser inferida com segurança. Não invente comportamento do domínio.

## 10. Critério de aplicação

As regras marcadas como obrigatórias definem o padrão do time. Recomendações podem ser adaptadas quando a complexidade ou as restrições do projeto justificarem. Explique desvios relevantes e mantenha as decisões consistentes com os contratos, a segurança, a testabilidade e a operação do sistema.
