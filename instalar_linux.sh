#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
    echo "Instale Python 3.9 ou superior pelo gerenciador de pacotes do seu Linux."
    exit 1
fi
python3 instalar.py "$@"
