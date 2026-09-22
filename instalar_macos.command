#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
    echo "Instale Python 3.9 ou superior em https://www.python.org/downloads/"
    read -r -p "Pressione Enter para sair..."
    exit 1
fi
python3 instalar.py "$@"
resultado=$?
if [ "$resultado" -ne 0 ]; then
    read -r -p "Pressione Enter para sair..."
fi
exit "$resultado"
