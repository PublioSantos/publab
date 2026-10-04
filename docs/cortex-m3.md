[English](cortex-m3.md) | [Português](cortex-m3.pt_BR.md)

# Cortex-M3 — educational model

## ⚠️ Simplified implementation for learning — not production-compatible code

The ARM Cortex-M3 module of PubLab is a **teaching model**, not an emulator
and not a development tool for real ARM hardware.

- A program that runs here is **not** guaranteed to behave the same way on a
  physical Cortex-M3, and must never be used as a reference for firmware,
  certification, timing analysis or any production decision.
- Only an explicitly documented subset of the Thumb instruction set will be
  modelled. What is outside that subset is **absent, not approximated**.
- Peripherals (GPIO, UART, SysTick, Timer) will be marked `conceptual` or
  `based on <specific MCU>`. **No peripheral address is invented.** The
  Cortex-M3 core defines very little of what a board exposes; whenever a real
  register or address is used, the specific part is named.
- Interrupt latency, cycle counts, the memory protection unit, caches and
  electrical behaviour are **not** modelled.
- Any future export to real hardware (phase 12) must state the MCU and target
  explicitly.

## Status: not implemented

Nothing of the Cortex-M3 exists in the code yet. It is phase 10 of the
development order. This page records the boundary before any code is written.

## Planned scope

The architecture as it will be presented (sections 31-32 of the
specification):

```
Registers    R0-R12, R13 = SP, R14 = LR, R15 = PC
Flags        N, Z, C, V
Peripherals  GPIO, UART, SysTick, Timer   (conceptual, or a named MCU)
```
