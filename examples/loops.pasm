; loops.pasm — a countdown, built from SUB, JZ and JMP.
;
; The Basic Mode set has no JNZ (that is Advanced Mode, phase 8), so the loop
; tests for zero and jumps out, then jumps back unconditionally.
;
; Output: 3, 2, 1, 0
;
; --- Português ---
;
; loops.pasm — uma contagem regressiva, construída com SUB, JZ e JMP.
;
; O conjunto do Basic Mode não tem JNZ (isso é Advanced Mode, fase 8), então
; o laço testa se é zero e salta pra fora, depois salta de volta sem
; condição.
;
; Saída: 3, 2, 1, 0

    LOAD A, 3
loop:
    PRINT A
    SUB A, 1
    JZ done
    JMP loop
done:
    PRINT A
    HALT
