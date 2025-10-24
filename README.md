# 🤖 AI Commit Script

Um script em Python que gera mensagens de commit automáticas com base nas mudanças do código (git diff), usando modelos de IA (Ollama ou OpenAI).  
Ele segue o padrão Semantic Commit Messages e inclui suporte a autoatualização via GitHub.

---

## 🚀 Recursos

- Autoatualização: verifica automaticamente se há uma nova versão no GitHub (máx. 1 vez por dia para evitar limites de requisição).  
- Geração de commits com IA:
  - Suporte a Ollama (qwen2.5-coder, codellama, etc)
  - Suporte a OpenAI GPT (gpt-4, gpt-5-mini, etc)
- Analisa:
  - Mudanças (git diff)
  - Arquivos modificados
  - Commits recentes (para entender o estilo)
- Gera várias sugestões de commit para escolher.
- Commita direto no Git se aprovado.

---

## 🛠️ Instalação

### 1. Via script oficial (install.sh)

Você pode instalar de forma global no terminal sem precisar de sudo:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/WildesPiva/ai-commit-script/main/install.sh)"
```

Alternativa com wget:

```bash
bash -c "$(wget -qO- https://raw.githubusercontent.com/WildesPiva/ai-commit-script/main/install.sh)"
```

O script faz:
1. Cria ~/.local/bin (se não existir)  
2. Move o ai-commit.py para lá  
3. Dá permissão de execução  
4. Adiciona ~/.local/bin ao PATH do usuário se necessário  

Depois disso, você poderá rodar o comando globalmente:

```bash
ai-commit
```
---

### 2. Manual (opcional)

1. Baixe o script:

```bash
curl -fsSL https://raw.githubusercontent.com/WildesPiva/ai-commit-script/main/ai-commit.py -o ~/ai-commit
```

2. Mova para ~/.local/bin:

```bash
mkdir -p ~/.local/bin
mv ~/ai-commit ~/.local/bin/ai-commit
chmod +x ~/.local/bin/ai-commit
```

3. Verifique se ~/.local/bin está no PATH:

```bash
echo $PATH | grep -q "$HOME/.local/bin" && echo "PATH OK" || echo "Adicione export PATH=\"$HOME/.local/bin:\$PATH\" ao seu shell"
```

4. Execute:

```bash
ai-commit
```

---

## ⚙️ Uso

1. Faça suas alterações normalmente:

```bash
git add .
```

2. Rode o script:

```bash
ai-commit
```

3. Escolha uma das sugestões ou regenere:

📂 Staged Files:
  - src/utils/helpers.ts
  - src/pages/login.tsx

📝 Generating commit messages...

✨ Generated Commit Messages:

1. feat(auth): add user session persistence on login
2. fix(utils): handle edge case for empty email input
3. refactor: simplify login validation logic
4. style: format auth utils with consistent casing
5. chore: update imports and minor cleanups

Choose a commit message (1–5) [r] regenerate / [c] cancel:

---

## 🔁 Atualização automática

O script verifica diariamente se há uma nova versão no GitHub.  
Se houver, ele faz backup automático e atualiza o arquivo.  
Caso o script esteja em um diretório sem permissão de escrita, ele exibirá uma mensagem clara para você mover para ~/.local/bin.

---

## 🧩 Argumentos de linha de comando

Argumento | Descrição | Padrão
-----------|-----------|--------
--model | Modelo a usar (Ollama ou OpenAI) | qwen2.5-coder:3b
--recent-commits | Número de commits recentes usados como contexto ou no para desativar | 5
--commits | Quantas sugestões de commit gerar | 5

Exemplo:
```bash
ai-commit --model gpt-5-mini --recent-commits 10 --commits 3
```
---

## 🧾 Licença

MIT © Wildes Piva (https://github.com/wildespiva)
