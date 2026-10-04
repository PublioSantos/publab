; hello.pasm — the smallest complete PubASM program.
;
; The PubVM has no character output: PRINT shows the VALUE of a register
; (section 13 of the specification), so this program prints 1, not a greeting.
; Run it with Step to watch PC move from 0x0000 to 0x0003 to 0x0005.
;
; --- Português ---
;
; hello.pasm — o menor programa completo em PubASM.
;
; A PubVM não tem saída de caractere: o PRINT mostra o VALOR de um registrador
; (seção 13 da especificação), então este programa imprime 1, não uma
; saudação. Rode com Step para ver o PC andar de 0x0000 para 0x0003 e 0x0005.

    LOAD A, 1
    PRINT A
    HALT
