[English](cortex-m3.md) | [Português](cortex-m3.pt_BR.md)

# Cortex-M3 — modelo educacional

## ⚠️ Implementação simplificada para aprendizado, não código compatível com produção

O módulo ARM Cortex-M3 do PubLab é um **modelo de ensino**, não um emulador e
não uma ferramenta de desenvolvimento para hardware ARM real.

- Um programa que roda aqui **não** tem garantia de se comportar igual em um
  Cortex-M3 físico, e nunca deve ser usado como referência para firmware,
  certificação, análise de temporização ou qualquer decisão de produção.
- Apenas um subconjunto explicitamente documentado do conjunto Thumb será
  modelado. O que está fora dele está **ausente, não aproximado**.
- Periféricos (GPIO, UART, SysTick, Timer) serão marcados como `conceitual` ou
  `baseado em <MCU específico>`. **Nenhum endereço de periférico é inventado.**
  O núcleo Cortex-M3 define muito pouco do que uma placa expõe; sempre que um
  registrador ou endereço real for usado, a peça específica será nomeada.
- Latência de interrupção, contagem de ciclos, unidade de proteção de memória,
  caches e comportamento elétrico **não** são modelados.
- Qualquer exportação futura para hardware real (fase 12) precisa declarar
  explicitamente o MCU e o target.

## Situação: não implementado

Nada do Cortex-M3 existe no código ainda. É a fase 10 da ordem de
desenvolvimento. Esta página registra a fronteira antes de qualquer linha de
código.

## Escopo previsto

A arquitetura como será apresentada (seções 31-32 da especificação):

```
Registradores  R0-R12, R13 = SP, R14 = LR, R15 = PC
Flags          N, Z, C, V
Periféricos    GPIO, UART, SysTick, Timer   (conceitual, ou um MCU nomeado)
```
