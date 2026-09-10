import os
import json
import subprocess

def read_code(file_path: str) -> dict:
    """Lê o conteúdo de um arquivo de código a partir do caminho informado.

    Args:
        file_path: caminho completo (ou relativo ao diretório atual) do
            arquivo a ser lido.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"error": f"Arquivo não encontrado: {file_path}"}


def detect_test_setup(project_path: str=".") -> dict:
    """Detecta o tipo de projeto Node (Nest, Express, Fastify, vanilla) e o
    test runner configurado (Jest, Vitest, Mocha), lendo o package.json.

    Args:
        project_path: diretório raiz do projeto a inspecionar.
    """
    pkg_path = os.path.join(project_path, "package.json")
    if not os.path.exists(pkg_path):
        return {"error": f"package.json não encontrado em {project_path}"}

    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    # 1. Estilo do projeto (mais específico primeiro)
    if "@nestjs/core" in deps:
        style = "nest"
    elif "fastify" in deps:
        style = "fastify"
    elif "express" in deps:
        style = "express"
    else:
        style = "plain-node"

    # 2. Test runner
    if "vitest" in deps:
        runner = "vitest"
        run_cmd = "npx vitest run"
    elif "mocha" in deps:
        runner = "mocha"
        run_cmd = "npx mocha"
    elif "jest" in deps:
        runner = "jest"
        run_cmd = "npx jest"
    else:
        runner = None
        run_cmd = None

    return {
        "style": style,
        "test_runner": runner,
        "run_cmd": run_cmd,
        "has_typescript": "typescript" in deps,
    }

def run_tests(project_path: str=".", test_path: str = None) -> dict:
    """Executa os testes do projeto usando o test runner detectado
    (jest/vitest/mocha) e retorna se passou ou falhou, com os logs.

    Args:
        project_path: diretório raiz do projeto onde rodar os testes.
        test_path: caminho de um arquivo/pasta de teste específico
            (opcional — se omitido, roda a suíte inteira).
    """
    setup = detect_test_setup(project_path)
    if setup.get("error"):
        return setup
    if not setup.get("run_cmd"):
        return {"error": "Nenhum test runner (jest/vitest/mocha) detectado."}

     #Guard-rail: evita travar em npx tentando instalar pacote na hora
    if setup["test_runner"] in ("jest", "vitest", "mocha"):
        if not os.path.isdir(os.path.join(project_path, "node_modules")):
            return {
                "error": (
                    "node_modules não encontrado. Chame install_dependencies "
                    "antes de rodar os testes."
                )
            }    

    cmd = setup["run_cmd"].split()
    if test_path:
        cmd.append(test_path)

    timeout = int(os.getenv("TEST_TIMEOUT_SECONDS", "120"))

    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"Testes excederam {timeout}s e foram interrompidos."}

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout[-3000:],
        "stderr": result.stderr[-3000:],
    }

def write_test_file(file_path: str, content: str, overwrite: bool = False) -> dict:
    """Grava o conteúdo de um arquivo de teste no caminho informado.

    Args:
        file_path: caminho completo (ou relativo) de onde salvar o teste,
            incluindo o nome do arquivo (ex: ./code.test.js).
        content: conteúdo do arquivo de teste a ser escrito.
        overwrite: se False (padrão) e já existir um arquivo nesse caminho,
            não sobrescreve — retorna um aviso para o agente decidir o que fazer.
    """
    if os.path.exists(file_path) and not overwrite:
        return {
            "warning": (
                f"Já existe um arquivo em {file_path}. Chame novamente com "
                "overwrite=True se quiser sobrescrever."
            )
        }

    os.makedirs(os.path.dirname(os.path.abspath(file_path)) or ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"success": True, "path": file_path}

def install_dependencies(project_path: str) -> dict:
    """Instala as dependências do projeto (executa npm install) antes de
    rodar os testes, quando node_modules ainda não existe.

    Args:
        project_path: diretório raiz do projeto (onde está o package.json).
    """
    if not os.path.exists(os.path.join(project_path, "package.json")):
        return {"error": f"package.json não encontrado em {project_path}"}

    timeout = int(os.getenv("INSTALL_TIMEOUT_SECONDS", "180"))
    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"npm install excedeu {timeout}s."}

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    }