# 🤖 AI Commit Script

Um script em Python que **gera mensagens de commit automáticas** com base nas mudanças do código (`git diff`), usando **modelos de IA** (Ollama ou OpenAI).  
Ele segue o padrão **Semantic Commit Messages** e inclui suporte a **autoatualização via GitHub**.

---

## 🚀 Recursos

- 🔍 **Autoatualização**: verifica automaticamente se há uma nova versão no GitHub.
- 🤖 **Geração de commits com IA**:
  - Suporte a **Ollama** (`qwen2.5-coder`, `codellama`, etc)
  - Suporte a **OpenAI GPT** (`gpt-4`, `gpt-5`, etc)
- 🧠 Analisa:
  - Mudanças (`git diff`)
  - Arquivos modificados
  - Commits recentes (para entender o estilo)
- 💬 Gera **várias sugestões** de commit para escolher.
- ✅ Commita direto no Git se aprovado.

---

## 🛠️ Instalação

1. **Baixe o script:**

```bash
curl -O https://raw.githubusercontent.com/wildespiva/ai-commit-script/main/ai-commit.py
chmod +x ai-commit.py
