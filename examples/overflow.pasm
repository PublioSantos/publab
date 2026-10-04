; overflow.pasm — the same program gives a different answer on a different
; machine. This is the Golden Test of the specification (sections 18 and 48).
;
; PubVM-8:   A = 14,  C = 1    (270 does not fit in 8 bits)
; PubVM-16:  A = 270, C = 0
; PubVM-32:  A = 270, C = 0
;
; Phases 1-2 implement and validate PubVM-8; the 16- and 32-bit variants are
; the same core with a different word size (phases 3-4).

    LOAD A, 250
    LOAD B, 20
    ADD A, B
    PRINT A
    HALT
