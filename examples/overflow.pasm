; overflow.pasm — the same program gives a different answer on a different
; machine. This is the Golden Test of the specification (sections 18 and 48).
;
; PubVM-8:   A = 14,  C = 1    (270 does not fit in 8 bits)
; PubVM-16:  A = 270, C = 0
; PubVM-32:  A = 270, C = 0
;
; All three are the same core with a different word size. The test suite runs
; this very file on each of them and checks the three answers above.
;
; --- Português ---
;
; overflow.pasm — o mesmo programa dá uma resposta diferente numa máquina
; diferente. Este é o Golden Test da especificação (seções 18 e 48).
;
; PubVM-8:   A = 14,  C = 1    (270 não cabe em 8 bits)
; PubVM-16:  A = 270, C = 0
; PubVM-32:  A = 270, C = 0
;
; As três são o mesmo núcleo com um tamanho de palavra diferente. A suíte de
; testes roda este mesmo arquivo em cada uma delas e confere as três
; respostas acima.

    LOAD A, 250
    LOAD B, 20
    ADD A, B
    PRINT A
    HALT
