"""Prepara o ambiente isolado e inicia a interface nos tres sistemas."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

PASTA = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Instalar e abrir o Vigenere Lab")
    parser.add_argument("--preparar", action="store_true", help="Preparar sem abrir o programa")
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        raise RuntimeError("Instale Python 3.9 ou superior e execute novamente.")
    for nome in ("vigenere_web.py", "vigenere_core.py", "interface.html", "requirements.txt"):
        if not (PASTA / nome).is_file():
            raise RuntimeError(f"Arquivo ausente: {nome}. Extraia o ZIP completo antes de instalar.")

    ambiente = PASTA / ".venv"
    executavel = ambiente / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not ambiente.exists():
        print("Criando ambiente virtual .venv...", flush=True)
        try:
            venv.EnvBuilder(with_pip=True).create(ambiente)
        except Exception as erro:
            raise RuntimeError(
                "Nao foi possivel criar a venv. No Debian/Ubuntu, instale python3-venv. "
                "Confira tambem a permissao de escrita nesta pasta. "
                f"Detalhes: {erro}"
            ) from erro
    if not executavel.is_file():
        raise RuntimeError("A .venv existente esta incompleta ou veio de outro sistema. "
                           "Renomeie essa pasta e execute novamente.")
    # Equivalente a ativar a venv no terminal, restrito ao processo iniciado.
    variaveis = os.environ.copy()
    variaveis["VIRTUAL_ENV"] = str(ambiente)
    variaveis["PATH"] = str(executavel.parent) + os.pathsep + variaveis.get("PATH", "")
    variaveis.pop("PYTHONHOME", None)
    variaveis.pop("PYTHONPATH", None)
    print("Verificando dependencias...", flush=True)
    subprocess.run([str(executavel), "-m", "pip", "install", "--disable-pip-version-check",
                    "--no-index", "-r", str(PASTA / "requirements.txt")],
                   cwd=PASTA, env=variaveis, check=True)
    print("Ambiente pronto. Este projeto nao precisa de pacotes externos.", flush=True)
    if not args.preparar:
        print("Abrindo o navegador. Para encerrar, pressione Ctrl+C neste terminal.", flush=True)
        subprocess.run([str(executavel), str(PASTA / "vigenere_web.py")],
                       cwd=PASTA, env=variaveis, check=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    except (RuntimeError, OSError, subprocess.CalledProcessError) as erro:
        print(f"\nErro: {erro}", file=sys.stderr)
        sys.exit(1)
