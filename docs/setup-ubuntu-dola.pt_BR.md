# Configuração no Ubuntu + Dola (Assistente IA) para Desenvolvimento

## 1. Ambiente no Ubuntu — Pré-requisitos

Instale as ferramentas essenciais:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl python3 python3-pip pipx build-essential
pipx ensurepath
```

Reinicie o terminal após rodar.

### Ferramentas de IA locais recomendadas

```bash
# Ollama (executa modelos LLM localmente)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1  # ou codellama para foco em código
ollama serve &
```

---

## 2. Fluxo de Prompt — Como usar com Dola

Modelo de prompt estruturado otimizado para desenvolvimento no Ubuntu:

```
[CONTEXTO]
Sistema: Ubuntu 22.04/24.04
Projeto: <nome do seu projeto>
Stack: <linguagens, ferramentas, versões>
Objetivo: <o que você quer construir/resolver>

[INSTRUÇÕES]
- Responda com comandos prontos para copiar e executar
- Inclua verificação de erros e tratamento de exceções
- Mantenha compatibilidade com shell bash
- Explique cada bloco de forma concisa
- Use português na conversa e código em inglês

[TAREFA]
<descreva o que precisa fazer: instalar, configurar, codificar, depurar>
```

---

## 3. Exemplos Prontos de Uso

**Exemplo A — Criar/otimizar script shell**

> "Dola, preciso de um script bash no Ubuntu que faça backup de um diretório, comprima em `.tar.gz`, registre log e envie para um diretório de destino. Inclua verificação de espaço em disco e tratamento de erros."

**Exemplo B — Configurar ambiente dev**

> "Dola, monte o passo a passo para configurar ambiente de desenvolvimento Python + Node.js no Ubuntu, com versões específicas, gerenciadores de versão e verificação de integridade."

**Exemplo C — Depurar/otimizar código**

> "Dola, este código está apresentando erro `<mensagem>` no Ubuntu. Analise, identifique a causa raiz, proponha a correção e valide o comando de teste."

---

## 4. Integração com VS Code

- Extensão **Dola AI** (`dolaai`) — funciona no Linux/Ubuntu
- Ou use **Aider** (via Ollama local):

```bash
pipx install aider-chat
aider --model ollama/llama3.1 seu_arquivo.py
```
