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