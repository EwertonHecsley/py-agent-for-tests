# Agente de testes com Google ADK

Um agente em Python, construído com o [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/), para apoiar a criação e a validação de testes em projetos Node.js. Ele lê o código do projeto, identifica a stack de testes, pode gerar arquivos de teste e executa a suíte para que você itere até obter uma cobertura confiável.

> **Objetivo:** reduzir o trabalho repetitivo de escrever testes unitários e de ponta a ponta (E2E), sem substituir a revisão humana sobre os cenários e as regras de negócio cobertas.

## O que o agente faz

O agente disponibiliza as seguintes ferramentas ao modelo:

| Ferramenta | Uso |
| --- | --- |
| `read_code` | Lê um arquivo do projeto para que o agente entenda a implementação a testar. |
| `detect_test_setup` | Inspeciona o `package.json` e identifica NestJS, Express, Fastify ou Node.js puro; também detecta Jest, Vitest ou Mocha. |
| `write_test_file` | Cria um arquivo de teste e protege arquivos existentes por padrão. |
| `install_dependencies` | Executa `npm install` quando o projeto alvo ainda não possui `node_modules`. |
| `run_tests` | Executa Jest, Vitest ou Mocha e devolve o resultado e os trechos finais dos logs. |

Com uma boa instrução, ele pode ajudar a gerar:

- **Testes unitários:** funções, serviços, controladores e casos de erro, usando mocks quando necessário;
- **Testes E2E:** fluxos HTTP, integração entre camadas e cenários de sucesso e falha;
- **Testes de regressão:** casos reproduzíveis para bugs corrigidos.

## Pré-requisitos

- Python 3.10 ou superior;
- Node.js e npm disponíveis no ambiente onde ficam os projetos que serão testados;
- Uma chave compatível com o modelo configurado no Google ADK (por exemplo, Google AI Studio ou Vertex AI);
- Acesso de leitura e escrita ao projeto alvo — o agente precisa ler código e poderá criar arquivos de teste.

## Instalação

Clone o repositório e crie um ambiente virtual Python:

```bash
git clone <URL_DO_SEU_FORK>
cd py-agent-for-tests

python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install google-adk python-dotenv
```

Em seguida, crie o seu arquivo de configuração local:

```bash
cp .env.example .env
```

> O arquivo `.env` contém credenciais e já é ignorado pelo Git. Nunca publique sua chave de API.

## Configuração

Edite o arquivo `.env` criado no passo anterior:

```dotenv
# Para Google AI Studio
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Escolha um modelo disponível na sua conta
MODEL_NAME=gemini-2.5-flash

# Instruções de comportamento do agente; use \n para quebras de linha
AGENT_INSTRUCTION=Você é um especialista em testes Node.js.\nAntes de criar arquivos, leia o código e detecte a configuração de testes.\nCrie testes unitários e E2E quando forem apropriados.\nNão sobrescreva arquivos existentes sem confirmação.\nExecute os testes criados e corrija falhas relacionadas a eles.
```

Para usar **Vertex AI**, defina `GOOGLE_GENAI_USE_VERTEXAI=TRUE` e configure as credenciais e o projeto do Google Cloud exigidos pelo seu ambiente. Consulte a documentação do ADK para os detalhes de autenticação.

### Instrução recomendada

A variável `AGENT_INSTRUCTION` é obrigatória: o projeto não inicia se ela estiver ausente. Mantenha nela regras claras, como as abaixo:

1. Inspecionar a implementação e os testes existentes antes de escrever código;
2. Preservar o padrão de testes e a estrutura de diretórios do projeto alvo;
3. Cobrir casos de sucesso, borda e erro;
4. Para E2E, não usar serviços externos reais sem autorização; preferir ambiente, banco e credenciais de teste;
5. Executar apenas os testes relevantes primeiro e informar qualquer falha que já existia.

## Como executar

O pacote expõe `root_agent`, a instância que o Google ADK pode carregar. Com o ambiente virtual ativado e o `.env` configurado, inicie a interface de desenvolvimento do ADK:

```bash
adk web
```

No seletor de agentes, escolha este diretório/projeto e use o agente `test_assistant`. Caso prefira uma integração própria, importe a instância Python:

```python
from agent import root_agent

# Passe root_agent ao runner ou à aplicação ADK que você utiliza.
```

## Exemplo de conversa

Depois de apontar o agente para o diretório do projeto alvo, envie um pedido específico, por exemplo:

> Analise `src/services/user.service.ts`, descubra qual runner está configurado e crie testes unitários para criação de usuário, e-mail duplicado e validação inválida. Salve-os no padrão já usado no projeto. Execute somente o novo arquivo de teste e mostre o resultado.

Para um teste E2E:

> No projeto em `../minha-api`, identifique a configuração de testes e crie testes E2E para `POST /users`: criação válida, payload inválido e e-mail duplicado. Use somente recursos de teste, não o banco de produção. Execute os testes criados.

Quanto mais contexto você fornecer — arquivos, endpoints, regras de negócio, convenções e ambiente de teste — mais precisos serão os casos gerados.

## Projetos e runners reconhecidos

`detect_test_setup` lê as dependências de `package.json` e reconhece:

| Categoria | Valores reconhecidos |
| --- | --- |
| Estilo de projeto | NestJS, Fastify, Express e Node.js puro |
| Runner | Vitest, Mocha e Jest |
| Linguagem | TypeScript, quando `typescript` está nas dependências |

O comando de execução é `npx vitest run`, `npx mocha` ou `npx jest`, conforme o runner encontrado. Sem `node_modules`, o agente solicita a execução de `install_dependencies` antes de rodar a suíte.

## Segurança e boas práticas

- **Revise sempre os testes gerados.** Eles podem ter premissas incorretas sobre regras de negócio, mocks ou infraestrutura.
- **Use um projeto de teste.** As ferramentas recebem caminhos de arquivo e diretório; não aponte o agente para código ou dados de produção.
- **Evite segredos nos prompts e fixtures.** Use variáveis de ambiente e credenciais descartáveis para integrações E2E.
- **Confirme sobrescritas.** `write_test_file` não substitui um arquivo existente a menos que seja chamado explicitamente com `overwrite=True`.
- **Controle o tempo de execução.** `TEST_TIMEOUT_SECONDS` limita testes (padrão: 120 segundos) e `INSTALL_TIMEOUT_SECONDS` limita o `npm install` (padrão: 180 segundos).
- **Entenda o escopo atual.** A detecção e a execução automatizada são focadas em projetos Node.js e nos runners listados acima. Frameworks de navegador, bancos de dados e serviços externos podem exigir instruções, configuração e fixtures adicionais no projeto alvo.

## Solução de problemas

| Mensagem ou sintoma | Como resolver |
| --- | --- |
| `AGENT_INSTRUCTION não definida no .env` | Crie `.env` a partir de `.env.example` e preencha a variável. |
| `package.json não encontrado` | Informe o diretório raiz correto do projeto Node.js ao agente. |
| `Nenhum test runner ... detectado` | Instale/configure Jest, Vitest ou Mocha no projeto alvo. |
| `node_modules não encontrado` | Execute `install_dependencies` ou rode `npm install` no projeto alvo. |
| Testes excederam o limite | Ajuste `TEST_TIMEOUT_SECONDS` no `.env` ou investigue testes lentos/travados. |
| O agente não consegue usar o modelo | Verifique `GOOGLE_API_KEY`, `MODEL_NAME` e o modo Google AI Studio/Vertex AI. |

## Estrutura do repositório

```text
.
├── agent/
│   ├── agent.py       # Configuração e instruções do agente ADK
│   ├── tools.py       # Ferramentas de leitura, geração e execução de testes
│   └── __init__.py    # Exporta root_agent
├── .env.example       # Modelo de variáveis de ambiente
└── README.md          # Esta documentação
```

## Contribuições

Contribuições são bem-vindas. Antes de abrir uma mudança, descreva o comportamento esperado, mantenha a documentação atualizada e valide que os módulos Python continuam compilando:

```bash
python -m compileall agent
```

Ideias úteis incluem suporte a outros runners, templates de instrução por framework, execução isolada de E2E e relatórios de cobertura.
