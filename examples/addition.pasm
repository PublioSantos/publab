; addition.pasm — add two registers and look at the result.
;
; On PubVM-8:  A = 30, C = 0, Z = 0, N = 0, O = 0

    LOAD A, 10
    LOAD B, 20
    ADD A, B
    PRINT A
    HALT
