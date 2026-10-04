[English](README.md) | [Português](README.pt_BR.md)

# Examples

Every program here really runs: `tests/examples_test.kf` assembles each file
for PubVM-8, executes it and asserts its output. An example that stopped
working would fail the test suite.

| File | What it shows |
|---|---|
| `hello.pasm` | the smallest complete program |
| `addition.pasm` | ADD between two registers |
| `overflow.pasm` | the Golden Test: the word size changes the answer |
| `loops.pasm` | a loop with SUB, JZ and JMP |
| `memory.pasm` | STORE and LOAD through memory |

The specification also lists `stack.pasm` and `call-return.pasm`. Those need
PUSH/POP/CALL/RET, which belong to Advanced Mode (phase 8) and are **not
implemented yet** — so they are not here. The assembler rejects those
instructions with diagnostic `ASM010`, saying exactly that, instead of
pretending they exist.
