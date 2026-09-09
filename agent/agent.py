import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from .tools import read_code, detect_test_setup

# Carrega as variáveis do .env para o ambiente do processo
load_dotenv()

def _load_instruction() -> str:
    raw = os.getenv("AGENT_INSTRUCTION", "")
    if not raw:
        raise RuntimeError("AGENT_INSTRUCTION não definida no .env")
    return raw.replace("\\n", "\n")

root_agent = Agent(
    name="test_assistant",
    model=os.getenv("MODEL_NAME"),
    description="Assistente para criação e validação de testes",
    instruction=_load_instruction(),
    tools=[read_code, detect_test_setup]
)