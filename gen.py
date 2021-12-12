#!/usr/bin/env python3
import sys
import os

def pre(out):
    print("\n".join((
        "%define SYS_READ 0",
        "%define SYS_WRITE 1",
        "%define SYS_EXIT 60",
        "%define FD_STDIN 0",
        "%define FD_STDOUT 1",
        "",
        "section .data",
        "    mem: times 30000 db 0",
        "    memptr: dq 0",
        "",
        "section .text",
        "    global _start",
        "",
        "_start:",
        "    mov qword [memptr], mem",
    )), file=out)

def post(out):
    print("\n".join((
        "    mov ebx, 0",
        "    jmp exit",
        "",
        "exit:",
        "    mov rax, SYS_EXIT",
        "    syscall",
        "",
        "write:",
        "    mov rax, SYS_WRITE",
        "    mov rdi, FD_STDOUT",
        "    mov rsi, [memptr]",
        "    mov rdx, 1",
        "    syscall",
        "    ret",
        "",
        "read:",
        "    mov rax, SYS_READ",
        "    mov rdi, FD_STDIN",
        "    mov rsi, [memptr]",
        "    mov rdx, 1",
        "    syscall",
        "    cmp eax, 0",
        "    jnz SHORT readend",
        "    mov rax, [memptr]",
        "    mov byte [rax], 0",
        "readend:",
        "    ret",
    )), file=out)

def gen(inp, out):
    pre(out)

    loops = 0
    open_loops = []

    for c in inp.read():
        match c:
            case '>':
                print("    inc qword [memptr]", file=out)
            case '<':
                print("    dec qword [memptr]", file=out)
            case '[':
                loops += 1
                open_loops.append(loops)
                print("\n".join((
                    "",
                    f"loop{loops}:",
                    "    mov qword rax, [memptr]",
                    "    cmp byte [rax], 0",
                    f"    jz loop{loops}end",
                )), file=out)
            case ']':
                if len(open_loops) == 0:
                    print("Unexpected closing bracket", file=sys.stderr)
                    return
                loop = open_loops.pop()
                print("\n".join((
                    f"    jmp loop{loop}",
                    f"loop{loop}end:",
                )), file=out)
            case '+':
                print("\n".join((
                    "    mov qword rax, [memptr]",
                    "    inc qword [rax]",
                )), file=out)
            case '-':
                print("\n".join((
                    "    mov qword rax, [memptr]",
                    "    dec qword [rax]",
                )), file=out)
            case '.':
                print("    call write", file=out)
            case ',':
                print("    call read", file=out)

    post(out)

if __name__ == "__main__":
    match len(sys.argv):
        case 2:
            file = sys.argv[1]
            asmfile = file + ".asm"
            objfile = file + ".o"
            with open(asmfile, "w") as out:
                gen(sys.stdin, out)
        case 3:
            file = sys.argv[2]
            asmfile = file + ".asm"
            objfile = file + ".o"
            with open(sys.argv[1]) as inp:
                with open(asmfile, "w") as out:
                    gen(inp, out)
        case _:
            print("Invalid number of arguments", file=sys.stderr)
            exit()

    command = f"nasm -f elf64 {asmfile} -o {objfile}"
    print(command)
    if os.system(command) != 0:
        exit()

    command = f"ld {objfile} -o {file}"
    print(command)
    if os.system(command) != 0:
        exit()
