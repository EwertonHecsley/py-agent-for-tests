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


import os
import json


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

import subprocess

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