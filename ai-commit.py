#!/usr/bin/env python3
import re
import os
import sys
import urllib.request
import tempfile
import hashlib
import ollama
import subprocess
import argparse

from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))

# URL do script remoto no GitHub
REMOTE_URL = "https://raw.githubusercontent.com/wildespiva/ai-commit-script/main/ai-commit.py"

# Versão local (você pode atualizar manualmente aqui)
__version__ = "1.0.0"


def get_remote_version(code: str) -> str:
    """Extrai a versão do código remoto."""
    for line in code.splitlines():
        if line.startswith("__version__"):
            return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"


def download_remote_script() -> str:
    """Baixa o script remoto e retorna o conteúdo."""
    with urllib.request.urlopen(REMOTE_URL) as response:
        return response.read().decode("utf-8")


def update_script(new_code: str):
    """Substitui o arquivo atual pelo código novo."""
    script_path = os.path.abspath(sys.argv[0])
    backup_path = script_path + ".bak"

    # Cria backup
    os.rename(script_path, backup_path)
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(new_code)
        print(f"✅ Script atualizado com sucesso para a nova versão!")
        os.remove(backup_path)
        os.execv(sys.executable, [sys.executable, script_path] + sys.argv[1:])
    except Exception as e:
        print(f"❌ Erro ao atualizar: {e}")
        os.rename(backup_path, script_path)


def self_update():
    """Verifica e aplica atualização, se necessário."""
    try:
        print("🔍 Verificando nova versão...")
        remote_code = download_remote_script()
        remote_version = get_remote_version(remote_code)

        if remote_version > __version__:
            print(f"🚀 Nova versão encontrada ({remote_version}), atualizando...")
            update_script(remote_code)
        else:
            print(f"✅ Já está na versão mais recente ({__version__}).")
    except Exception as e:
        print(f"⚠️ Falha ao verificar atualização: {e}")



def clean_message(commit_message):
    """
    Extracts and cleans a commit message from any code block like:
    ```text codeblock!
    message
    ```
    or
    ```struct:
    message
    ```
    Returns the inner text; if no block exists, returns the original stripped string.
    """
    # Capture everything between the first ```... and the matching closing ```
    match = re.search(r"```[^\n]*\n([\s\S]*?)```", commit_message)
    if match:
        return match.group(1).strip()
    return commit_message.strip()


def get_staged_files():
    """Gets the list of staged files."""
    try:
        result = subprocess.run(["git", "diff", "--name-only", "--staged"], capture_output=True, text=True)
        staged_files = result.stdout.strip().split("\n")
        return staged_files if staged_files[0] else None
    except Exception as e:
        return [f"Error getting staged files: {str(e)}"]


def get_staged_diff():
    """Gets the Git diff of staged changes."""
    try:
        result = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
        git_diff = result.stdout.strip()
        return git_diff if git_diff else None
    except Exception as e:
        return f"Error getting diff: {str(e)}"


def get_recent_commits(count=5):
    """Gets recent commit messages for reference."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--pretty=format:%s"],
            capture_output=True,
            text=True
        )
        commits = result.stdout.strip().split("\n")
        return commits if commits[0] else []
    except Exception as e:
        return []


def get_original_files_content(staged_files):
    """Gets the original content of staged files for context."""
    files_content = {}
    for file in staged_files:
        try:
            # Get the file content from HEAD (before changes)
            result = subprocess.run(
                ["git", "show", f"HEAD:{file}"],
                capture_output=True,
                text=True,
                stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                files_content[file] = result.stdout
        except Exception:
            continue
    return files_content


def generate_commit_message(diff, staged_files, recent_commits, model):
    """Uses Ollama to generate a commit message following Copilot's structure."""
    
    # Build recent commits section
    recent_commits_text = "\n".join([f"- {commit}" for commit in recent_commits])
    
    # Build staged files section
    staged_files_text = "\n".join([f"  - {file}" for file in staged_files])
    
    # System message (following Copilot's structure)
    system_message = """You are an AI programming assistant, helping a software developer to come with the best git commit message for their code changes.
You excel in interpreting the purpose behind code changes to craft succinct, clear commit messages that adhere to the repository's guidelines.

# First, think step-by-step:
1. Analyze the CODE CHANGES thoroughly to understand what's been modified.
2. Use the ORIGINAL CODE to understand the context of the CODE CHANGES. Use the line numbers to map the CODE CHANGES to the ORIGINAL CODE.
3. Identify the purpose of the changes to answer the *why* for the commit messages, also considering the optionally provided RECENT USER COMMITS.
4. Review the provided RECENT REPOSITORY COMMITS to identify established commit message conventions. Focus on the format and style, ignoring commit-specific details like refs, tags, and authors.
5. Generate a thoughtful and succinct commit message for the given CODE CHANGES. It MUST follow the established writing conventions.
6. Remove any meta information like issue references, tags, or author names from the commit message. The developer will add them.
7. Now only show your message, wrapped with a single markdown ```text codeblock! Do not provide any explanations or details
8. Choose type based on code changes (feat, fix, docs, style, refactor, perf, test, or chore)
9. Do not copy the recent commits. 
Keep your answers short and impersonal."""

    # User message (following Copilot's structure)
    user_message = f"""<user-commits>
# RECENT USER COMMITS (For reference only, do not copy!):
{recent_commits_text if recent_commits_text else "- No recent commits found"}

</user-commits>
<recent-commits>
# RECENT REPOSITORY COMMITS (For reference only, do not copy!):
{recent_commits_text if recent_commits_text else "- No recent commits found"}

</recent-commits>
<changes>
<original-code>
# ORIGINAL CODE:
<attachment>
# Staged files:
{staged_files_text}
</attachment>

</original-code>
<code-changes>
# CODE CHANGES:
```diff
{diff}
```
</code-changes>

</changes>
<reminder>
Now generate a commit message that describes the CODE CHANGES.
DO NOT COPY commits from RECENT COMMITS, but use it as reference for the commit style.
ONLY return a single markdown code block, NO OTHER PROSE!
MODEL: type: message

commit message goes here

</reminder>
<custom-instructions>

</custom-instructions>"""

    # Make the API call with system and user messages

    if str(model).startswith('gpt'):
        response = client.responses.create(
            # model="gpt-5-mini",
            model=model,
            input=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
        )
        commit_message = response.output[-1].content[-1].text.strip()
    else:
        response = ollama.chat(
            # model='qwen2.5-coder:1.5b',
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            options={
                # "seed": None,         # força nova aleatoriedade (sem repetição)
                # "num_ctx": 0,         # garante que nenhum contexto anterior é usado
                # "cache": False,       # (algumas versões do Ollama ignoram isso, mas seguro incluir)
                # "temperature": 0.3    # opcional, ajuda a variar a resposta
            }
        )
        commit_message = response['message']['content'].strip()

    # Extract message from code block if present
    commit_message = clean_message(commit_message)
    
    # Ensure the response isn't empty or malformed
    if not commit_message:
        return "Auto-generated commit"

    return commit_message

def main():
    """CLI tool to generate Git commit messages from staged changes."""

    # -------------------------------
    # 🧠 CLI Arguments
    # -------------------------------
    parser = argparse.ArgumentParser(
        description="Generate semantic Git commit messages using AI."
    )
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:1.5b",
        help="Model to use for commit generation (default: qwen2.5-coder:1.5b)"
    )
    parser.add_argument(
        "--recent-commits",
        default="5",
        help="Number of recent commits for context, or 'no' to skip (default: 5)"
    )
    parser.add_argument(
        "--commits",
        type=int,
        default=5,
        help="Number of commit message suggestions to generate (default: 5)"
    )

    args = parser.parse_args()

    # -------------------------------
    # 🧩 Data loading
    # -------------------------------
    git_diff = get_staged_diff()
    staged_files = get_staged_files()

    if not git_diff:
        print("No staged changes found. Please stage changes using `git add .`")
        return

    print("\n📂 Staged Files:\n")
    for file in staged_files:
        print(f"  - {file}")

    # Recent commits (optional)
    recent_commits = []
    if args.recent_commits != "no":
        try:
            recent_commits = get_recent_commits(int(args.recent_commits))
        except ValueError:
            print("⚠️ Invalid value for --recent-commits. Use a number or 'no'.")
            return

    # -------------------------------
    # 🪄 Generation Function
    # -------------------------------
    def generate():
        print("\n📝 Generating commit messages...")
        commit_messages = []

        for i in range(args.commits):
            msg = generate_commit_message(
                git_diff, 
                staged_files, 
                recent_commits, 
                model=args.model
            )
            commit_messages.append(msg)

        print("\n✨ Generated Commit Messages:")
        for i, msg in enumerate(commit_messages, 1):
            print(f"\n{i}. {msg}")

        while True:
            choice = input(
                f"\nChoose a commit message (1-{args.commits}) "
                "[r] regenerate / [c] cancel: "
            ).strip().lower()

            if choice in {"c", "n"}:
                print("❌ Commit canceled.")
                return

            if choice in {"r", "regen", "regenerate"}:
                print("\n🔄 Regenerating commit messages...")
                return generate()

            if choice.isdigit() and 1 <= int(choice) <= args.commits:
                selected_message = commit_messages[int(choice) - 1]
                print(f"\n✅ Selected:\n\n\"{selected_message}\"")
                confirm = input("\nProceed with this commit? (y/n): ").strip().lower()

                if confirm == "y":
                    subprocess.run(["git", "commit", "-m", selected_message])
                    print("🎉 Commit created!")
                else:
                    print("❌ Commit canceled.")
                return

            print(f"⚠️ Invalid option. Please choose between 1–{args.commits}, r, or c.")

    generate()


if __name__ == "__main__":
    main()
