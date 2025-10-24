#!/usr/bin/env bash

# ======================================================
# AI Commit Script Installer
# Instala o script ai-commit.py globalmente para o usuário
# ======================================================

set -e

SCRIPT_NAME="ai-commit"
LOCAL_BIN="$HOME/.local/bin"
INSTALL_PATH="$LOCAL_BIN/$SCRIPT_NAME"

echo "📦 Instalando $SCRIPT_NAME..."

# 1️⃣ Cria ~/.local/bin se não existir
mkdir -p "$LOCAL_BIN"

# 2️⃣ Baixa o script diretamente do GitHub (última versão)
echo "🌐 Baixando o script do GitHub..."
curl -fsSL "https://raw.githubusercontent.com/wildespiva/ai-commit-script/main/ai-commit.py" -o "$INSTALL_PATH"

# 3️⃣ Dá permissão de execução
chmod +x "$INSTALL_PATH"
echo "✅ Script movido para $INSTALL_PATH e tornado executável."

# 4️⃣ Adiciona ao PATH se ainda não estiver
SHELL_RC="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if ! echo "$PATH" | grep -q "$LOCAL_BIN"; then
    echo "🛠️ Adicionando $LOCAL_BIN ao PATH no $SHELL_RC..."
    echo "" >> "$SHELL_RC"
    echo "# Adiciona ai-commit ao PATH" >> "$SHELL_RC"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
    echo "🔄 Atualize o shell ou rode: source $SHELL_RC"
fi

# 5️⃣ Verifica instalação
echo "🔍 Verificando instalação..."
if command -v "$SCRIPT_NAME" >/dev/null 2>&1; then
    echo "🎉 $SCRIPT_NAME instalado globalmente e pronto para usar!"
    echo "Execute com: $SCRIPT_NAME"
else
    echo "⚠️ Instalação concluída, mas não encontrado no PATH. Verifique se o shell foi reiniciado."
fi
