; memory.pasm — write a register to memory and read it back.
;
; Watch address 0x0080 in the memory view: it holds 2A (42) after the STORE.
; Output: 42

    LOAD A, 42
    STORE [0x80], A
    LOAD B, [0x80]
    PRINT B
    HALT
