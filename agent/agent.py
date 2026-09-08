import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from .tools import read_code

# Carrega as variáveis do .env para o ambiente do processo
load_dotenv()

root_agent = Agent(
    name="test_assistant",
    model=os.getenv("MODEL_NAME"),
    description="Assistente para criação e validação de testes",
    instruction=(
        "Você é um assistente de testes de software. Por enquanto, "
        "apenas responda de forma amigável confirmando que está no ar."
    ),
    tools=[read_code]
)