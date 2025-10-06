#!/bin/bash
cd /c/Trabalho/github/PyAmadon

echo "=== Testando PyAmadon no Git Bash ==="
echo "Diretório atual: $(pwd)"
echo "Versão do uv: $(uv --version)"

echo -e "\n=== Testando Python e PySide6 ==="
uv run python -c "import sys; print(f'Python: {sys.version}')"
uv run python -c "import PySide6; print(f'PySide6: {PySide6.__version__}')"

echo -e "\n=== Testando importação do main.py ==="
uv run python -c "import main; print('main.py importado com sucesso!')"

echo -e "\n=== Listando pacotes instalados ==="
uv pip list

echo -e "\n=== Teste concluído com sucesso! ==="