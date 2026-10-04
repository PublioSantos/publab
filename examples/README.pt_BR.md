[English](README.md) | [Português](README.pt_BR.md)

# Exemplos

Todo programa aqui realmente roda: `tests/examples_test.kf` monta cada arquivo
para a PubVM-8, executa e verifica a saída. Um exemplo que parasse de
funcionar quebraria a suíte de testes.

| Arquivo | O que mostra |
|---|---|
| `hello.pasm` | o menor programa completo |
| `addition.pasm` | ADD entre dois registradores |
| `overflow.pasm` | o Golden Test: o tamanho da palavra muda o resultado |
| `loops.pasm` | um laço com SUB, JZ e JMP |
| `memory.pasm` | STORE e LOAD passando pela memória |

A especificação também lista `stack.pasm` e `call-return.pasm`. Esses precisam
de PUSH/POP/CALL/RET, que pertencem ao Advanced Mode (fase 8) e **ainda não
estão implementados** — então não estão aqui. O assembler rejeita essas
instruções com o diagnóstico `ASM010`, dizendo exatamente isso, em vez de
fingir que existem.
