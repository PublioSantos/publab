# Ubuntu + Dola (AI Assistant) Setup for Development

## 1. Ubuntu Environment — Prerequisites

Install the essential tools:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl python3 python3-pip pipx build-essential
pipx ensurepath
```

Restart the terminal after running.

### Recommended local AI tools

```bash
# Ollama (runs LLM models locally)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1  # or codellama for code-focused tasks
ollama serve &
```

---

## 2. Prompt Flow — How to use Dola

Structured prompt template optimized for Ubuntu development:

```
[CONTEXT]
System: Ubuntu 22.04/24.04
Project: <your project name>
Stack: <languages, tools, versions>
Goal: <what you want to build/solve>

[INSTRUCTIONS]
- Reply with commands ready to copy and execute
- Include error checking and exception handling
- Keep bash shell compatibility
- Explain each block concisely
- Use your language in conversation, English in code

[TASK]
<describe what you need to do: install, configure, code, debug>
```

---

## 3. Ready-to-use Examples

**Example A — Create/optimize a shell script**

> "Dola, I need a bash script on Ubuntu that backs up a directory, compresses it to `.tar.gz`, logs the operation, and sends it to a destination directory. Include disk space checking and error handling."

**Example B — Set up a dev environment**

> "Dola, walk me through setting up a Python + Node.js development environment on Ubuntu, with specific versions, version managers, and integrity checks."

**Example C — Debug/optimize code**

> "Dola, this code is showing error `<message>` on Ubuntu. Analyze it, identify the root cause, propose a fix, and validate with a test command."

---

## 4. VS Code Integration

- **Dola AI** extension (`dolaai`) — works on Linux/Ubuntu
- Or use **Aider** (via local Ollama):

```bash
pipx install aider-chat
aider --model ollama/llama3.1 your_file.py
```
