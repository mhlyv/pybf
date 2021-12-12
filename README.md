# PYBF

Quick and dirty brainfuck compiler written in python. It outputs x86_64 linux assembly, and uses nasm.

## Examples

### cat

```
$ echo "+[,.]" | ./gen.py cat
nasm -f elf64 cat.asm -o cat.o
ld cat.o -o cat
$ cat cat.asm | ./cat        
%define SYS_READ 0
%define SYS_WRITE 1
%define SYS_EXIT 60
%define FD_STDIN 0
%define FD_STDOUT 1

section .data
    mem: times 30000 db 0
    memptr: dq 0

section .text
    global _start

_start:
   mov qword [memptr], mem
    mov qword rax, [memptr]
    inc qword [rax]

loop1:
    mov qword rax, [memptr]
    cmp byte [rax], 0
    jz loop1end
    call read
    call write
    jmp loop1
loop1end:
    mov ebx, 0
    jmp exit

exit:
    mov rax, SYS_EXIT
    syscall

write:
    mov rax, SYS_WRITE
    mov rdi, FD_STDOUT
    mov rsi, [memptr]
    mov rdx, 1
    syscall
    ret

read:
    mov rax, SYS_READ
    mov rdi, FD_STDIN
    mov rsi, [memptr]
    mov rdx, 1
    syscall
    cmp eax, 0
    jnz SHORT readend
    mov rax, [memptr]
    mov byte [rax], 0
readend:
    ret
```

### triangle

```
$ ./gen.py triangle.bf tri
nasm -f elf64 tri.asm -o tri.o
ld tri.o -o tri
$ ./tri 
                                *    
                               * *    
                              *   *    
                             * * * *    
                            *       *    
                           * *     * *    
                          *   *   *   *    
                         * * * * * * * *    
                        *               *    
                       * *             * *    
                      *   *           *   *    
                     * * * *         * * * *    
                    *       *       *       *    
                   * *     * *     * *     * *    
                  *   *   *   *   *   *   *   *    
                 * * * * * * * * * * * * * * * *    
                *                               *    
               * *                             * *    
              *   *                           *   *    
             * * * *                         * * * *    
            *       *                       *       *    
           * *     * *                     * *     * *    
          *   *   *   *                   *   *   *   *    
         * * * * * * * *                 * * * * * * * *    
        *               *               *               *    
       * *             * *             * *             * *    
      *   *           *   *           *   *           *   *    
     * * * *         * * * *         * * * *         * * * *    
    *       *       *       *       *       *       *       *    
   * *     * *     * *     * *     * *     * *     * *     * *    
  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *    
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *    
```
