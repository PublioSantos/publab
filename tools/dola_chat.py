#!/usr/bin/env python3
"""
Programa para enviar perguntas e capturar respostas do dola.com
Usa Playwright para automação do navegador.

Uso:
    python3 dola_chat.py "Qual é minha agenda de amanhã?"
    python3 dola_chat.py --interativo
"""

import asyncio
import sys
import argparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


DOLA_URL = "https://dola.com"

# Seletores CSS para elementos da interface do dola.com
# (ajuste conforme necessário após inspeção do site)
SELECTORS = {
    "chat_input":    'textarea, input[type="text"], [contenteditable="true"]',
    "send_button":   'button[type="submit"], button:has-text("Send"), button:has-text("Enviar")',
    "messages":      '[class*="message"], [class*="chat"], [class*="response"], [class*="bubble"]',
    "last_response": '[class*="assistant"], [class*="bot"], [class*="ai-message"]',
}


async def esperar_resposta(page, timeout_ms=30000):
    """Aguarda uma nova resposta aparecer na tela."""
    try:
        # Aguarda algum indicador de que a resposta chegou (typing indicator some)
        await page.wait_for_selector(
            '[class*="typing"], [class*="loading"], [class*="spinner"]',
            state="hidden",
            timeout=timeout_ms,
        )
    except PlaywrightTimeoutError:
        pass  # Pode não ter indicador de carregamento

    # Pequena pausa para garantir que o texto foi renderizado
    await asyncio.sleep(1.5)


async def capturar_ultima_resposta(page):
    """Captura o texto da última resposta do assistente."""
    # Tenta diferentes seletores para encontrar a resposta
    seletores_resposta = [
        '[data-role="assistant"]:last-child',
        '[class*="assistant"]:last-child',
        '[class*="bot-message"]:last-child',
        '[class*="ai"]:last-child',
        '[class*="response"]:last-child',
        '[class*="message"]:last-child',
    ]

    for seletor in seletores_resposta:
        try:
            elemento = page.locator(seletor).last
            if await elemento.count() > 0:
                texto = await elemento.inner_text()
                if texto.strip():
                    return texto.strip()
        except Exception:
            continue

    # Fallback: captura todo o conteúdo visível da área de chat
    try:
        conteudo = await page.inner_text('[class*="chat"], [class*="messages"], main')
        linhas = [l.strip() for l in conteudo.split('\n') if l.strip()]
        if linhas:
            return linhas[-1]
    except Exception:
        pass

    return "(não foi possível capturar a resposta)"


async def enviar_pergunta(page, pergunta: str) -> str:
    """Envia uma pergunta e retorna a resposta."""
    print(f"\n>> Pergunta: {pergunta}")

    # Localiza o campo de entrada
    input_field = page.locator(SELECTORS["chat_input"]).first
    await input_field.wait_for(state="visible", timeout=10000)

    # Limpa e preenche o campo
    await input_field.click()
    await input_field.fill(pergunta)

    # Envia com Enter ou clicando no botão
    try:
        send_btn = page.locator(SELECTORS["send_button"]).first
        if await send_btn.count() > 0 and await send_btn.is_visible():
            await send_btn.click()
        else:
            await input_field.press("Enter")
    except Exception:
        await input_field.press("Enter")

    # Aguarda a resposta
    await esperar_resposta(page)

    resposta = await capturar_ultima_resposta(page)
    print(f"<< Resposta: {resposta}\n")
    return resposta


async def iniciar_sessao(playwright, headless=True):
    """Inicia o navegador e abre o dola.com."""
    browser = await playwright.chromium.launch(
        headless=headless,
        executable_path="/opt/pw-browsers/chromium",
    )
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="pt-BR",
    )
    page = await context.new_page()

    print(f"Abrindo {DOLA_URL} ...")
    await page.goto(DOLA_URL, wait_until="networkidle", timeout=30000)

    # Aguarda a interface carregar
    await page.wait_for_timeout(2000)

    titulo = await page.title()
    print(f"Página carregada: {titulo}")

    return browser, context, page


async def modo_batch(perguntas: list[str], headless=True):
    """Envia uma lista de perguntas e retorna as respostas."""
    async with async_playwright() as pw:
        browser, context, page = await iniciar_sessao(pw, headless=headless)
        try:
            resultados = []
            for pergunta in perguntas:
                resposta = await enviar_pergunta(page, pergunta)
                resultados.append({"pergunta": pergunta, "resposta": resposta})
            return resultados
        finally:
            await browser.close()


async def modo_interativo(headless=False):
    """Modo interativo: lê perguntas do stdin e exibe respostas."""
    print("=== Modo Interativo — dola.com ===")
    print("Digite sua pergunta e pressione Enter. 'sair' para encerrar.\n")

    async with async_playwright() as pw:
        browser, context, page = await iniciar_sessao(pw, headless=headless)
        try:
            while True:
                try:
                    pergunta = input("Você: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nEncerrando...")
                    break

                if pergunta.lower() in ("sair", "exit", "quit"):
                    print("Encerrando...")
                    break

                if not pergunta:
                    continue

                await enviar_pergunta(page, pergunta)
        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Envia perguntas ao dola.com e captura respostas"
    )
    parser.add_argument(
        "pergunta",
        nargs="?",
        help="Pergunta a enviar (modo único)",
    )
    parser.add_argument(
        "--interativo", "-i",
        action="store_true",
        help="Modo interativo (chat contínuo)",
    )
    parser.add_argument(
        "--arquivo", "-f",
        help="Arquivo com perguntas (uma por linha)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Executar sem interface gráfica (padrão: False no interativo)",
    )
    args = parser.parse_args()

    if args.interativo:
        asyncio.run(modo_interativo(headless=args.headless))

    elif args.arquivo:
        with open(args.arquivo, encoding="utf-8") as f:
            perguntas = [l.strip() for l in f if l.strip()]
        resultados = asyncio.run(modo_batch(perguntas, headless=True))
        print("\n=== Resumo ===")
        for r in resultados:
            print(f"P: {r['pergunta']}")
            print(f"R: {r['resposta']}")
            print("-" * 40)

    elif args.pergunta:
        resultados = asyncio.run(modo_batch([args.pergunta], headless=True))
        if resultados:
            print(resultados[0]["resposta"])

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
