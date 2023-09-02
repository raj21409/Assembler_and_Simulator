import sys

xCoordinates = []
yCoordinates = []
cycle = 0

type={
    "10000":"A","10001":"A","10110":"A","11010":"A","11011":"A","11100":"A",
    "00000":"A","00001":"A",
    "10010":"B","11001":"B","11000":"B","00010":"B",
    "10011":"C","10111":"C","11101":"C","11110":"C",
    "10100":"D","10101":"D",
    "11111":"E","01100":"E","01101":"E",
    "01111":"E",
    "01010":"F"
    }                                                

registers={
    "000":"R0",
    "001":"R1",
    "010":"R2",
    "011":"R3",
    "100":"R4",
    "101":"R5",
    "110":"R6",
    "111":"FLAGS"
    }

reg_value=[]
for i in range(7):
    reg_value.append("0000000000000000")

count=0
mc=[]
mc = sys.stdin.read().splitlines()


count=len(mc)
memory=[]
x=count
for i in range(256):
    memory.append("0000000000000000")
j=0
for i in mc:
    if i!='':
        memory[j]=i
        j+=1


flags=[]
for i in range(16):
    flags.append('0')

reg_no={
        '000'  :0,
        '001'  :1,
        '010'  :2,
        '011'  :3,
        '100'  :4,
        '101'  :5,
        '110'  :6,
        '111'  :7
        }

def to16bit(num):
    if isinstance(num,int):
        x='{0:016b}'.format(num)
        return str(x)
    else:
        y = int(str(num),2)
        x='{0:016b}'.format(y)
        return str(x)

def to8bit(num):
    x='{0:08b}'.format(num)
    return str(x)


def store(register, ans):
    t = reg_no[register]
    if t==7:
        for i in range(16):
            flags[i] = ans[i]
    else:
        reg_value[t] = to16bit(ans)


def reg_file(register):
    t = reg_no[register]
    if t==7:
        return int(''.join(flags),2)
    return int(reg_value[t],2)


def float_file(register):
    t = reg_no[register]
    return float(int(reg_value[t],2))
    
def reset():
    for i in range(len(flags)):
        flags[i] = '0'

def ieeetodecimal(num):
    e=int(num[0:3],2)
    m=num[3:8]
    m=m+(7-len(m))*'0'
    s='1'+m[:e]+'.'+m[e:]
    k=s.index('.')
    d=int(s[:k],2)
    z=-1
    for i in s[k+1:]:
        d=d+(2**z)*int(i)
        z=z-1
    return d

def floattoieee(num):
    num = str(num)
    x = num.index('.')
    x1 = int(num[:x])
    x1 = to8bit(x1)
    if(float(num)>=1):
        x2 = x1.index('1')
    else:
        x2 = 0
        x1 = "0"
    x1 = x1[x2:]
    x1 = x1+'.'
    x3 = float(num[x:])
    while(x3!=1.0 and x3!=0.0):
        x3 = x3 * 2
        x4 = str(x3)
        x1 = x1 + x4[0]
    exp = x1.index('.') - 1
    x1 = x1.replace('.','')
    list1 = list(x1)
    list1.insert(1,'.')
    x1 = ''.join(list1)
    mantisaa = x1[2:7]
    exp = '{0:03b}'.format(exp)
    ans = exp + mantisaa
    while(len(ans)<8):
        ans = ans+'0'
    ans = "00000000"+ans
    return ans

def type_a(inst):
    op = inst[:5]
    r1 = inst[7:10]
    r2 = inst[10:13]
    r3 = inst[13:16]
    reset()
    if op=="10000":          #add
        ans = reg_file(r1) + reg_file(r2)
        if ans>65535:
            ans = ans%(65536)
            flags[12]='1'
        store(r3,ans)
    elif op=="10001":          #sub
        ans = reg_file(r1) - reg_file(r2)
        if ans<0:
            ans = 0
            flags[12]='1'
        store(r3,ans)
    elif op=="10110":            #mul
        ans = reg_file(r1) * reg_file(r2)
        if ans>65535:
            ans = ans%(65536)
            flags[12]='1'
        store(r3,ans)
    elif op=="11010":          #xor
        ans = reg_file(r1) ^ reg_file(r2)
        store(r3,ans)
        reset()
    elif op=="11011":           #or
        ans = reg_file(r1) | reg_file(r2)
        store(r3,ans)
        reset()
    elif op=="11100":          #and
        ans = reg_file(r1) & reg_file(r2)
        store(r3,ans)
        reset()
    elif op=="00000":        #addf
        t1=reg_no[r1]
        t2=reg_no[r2]
        reg1=ieeetodecimal(int(float(reg_value[t1])))
        reg2=ieeetodecimal(int(float(reg_value[t2])))
        ans=reg1+reg2
        if(ans>252):          #(2**7)(1.96875)
            flags[12]='1'
        ans = floattoieee(ans)
        store(r3,ans)
    elif op=="00001":        #subf
        t1=reg_no[r1]
        t2=reg_no[r2]
        reg1=ieeetodecimal(int(float(reg_value[t1])))
        reg2=ieeetodecimal(int(float(reg_value[t2])))
        ans=reg1-reg2
        if(ans<0):
            flags[12]='1'
            store(r3,0)
        else:
            ans = floattoieee(ans)
            store(r3,ans)



def type_b(inst):
    op = inst[:5]
    register = inst[5:8]
    imm = inst[8:16]
    if op=="10010":           #mov
        store(register,imm)
        reset()
    elif op=="11000":         #rs
        val = reg_file(register)
        imm = int(imm,2)
        ans = val>>imm
        store(register,ans)
        reset()
    elif op=="11001":         #ls
        val = reg_file(register)
        imm = int(imm,2)
        ans = val<<imm
        store(register,ans)
        reset()
    elif op=="00010":        #movf
        store(register,ieeetodecimal(imm))
        reset()


def type_c(inst):
    op = inst[:5]
    r1 = inst[10:13]
    r2 = inst[13:16]
    if op=="10011":            #mov
        ans = reg_file(r1)
        store(r2,ans)
        reset()
    elif op=="10111":         #div
        quotient = int(reg_file(r1)/reg_file(r2))
        remainder = int(reg_file(r1)%reg_file(r2))
        store("000",quotient)
        store("001",remainder)
        reset()
    elif op=="11101":          #invert
        ans = reg_file(r1)
        ans = to16bit(ans)
        ans = ans.replace('1', '2')
        ans = ans.replace('0', '1')
        ans = ans.replace('2', '0')
        store(r2,ans)
        reset()
    elif op=="11110":         #compare
        reset()
        if reg_file(r1)>reg_file(r2):
            flags[14]='1'
        elif reg_file(r1)<reg_file(r2):
            flags[13]='1'
        else:
            flags[15]='1'


def type_d(inst,pc):
    op = inst[:5]
    register = inst[5:8]
    addr = int(inst[8:16],2)
    if op=="10100":          #load
        ans = int(memory[addr],2)
        store(register,ans)
        xCoordinates.append(cycle)   
        yCoordinates.append(addr)
        reset()
    elif op=="10101":        #store
        ans = reg_file(register)
        ans = to16bit(ans)
        memory[addr] = ans
        xCoordinates.append(cycle)   
        yCoordinates.append(addr)
        reset()


def type_e(inst,pc):
    op = inst[:5]
    addr = int(inst[8:16],2)
    if op=="11111":        #jmp
        pc = addr
        reset()
    elif op=="01100":       #jlt 
        if(flags[13]=='1'):
            pc=addr
            reset()
    elif op=="01101":           #jgt
        if(flags[14]=='1'):
            pc=addr
            reset()
    elif op=="01111":           #je
        if(flags[15]=='1'):
            pc=addr
            reset()
    reset()
    return pc


def type_f(pc):
    reset()
    printsss(pc)
    for i in memory:
        if i=='':
            continue
        else:
            print(i)


def printsss(pc):
    pc = to8bit(pc)
    print(pc,end=" ")
    for i in reg_value:
        print(i,end=" ")
    for i in flags:
        print(i,end="")
    print()

    
typ = []
pc=0

while pc<=count:
    xCoordinates.append(cycle)   
    yCoordinates.append(pc)
    inst = memory[pc]
    opcode = inst[:5]
    typ = type[opcode]
    if typ=="A":
        type_a(inst)
    elif typ=="B":
        type_b(inst)
    elif typ=="C":
        type_c(inst)
    elif typ=="D":
        type_d(inst,pc)
    elif typ=="E":
        pc1=type_e(inst,pc)
        printsss(pc)
        if pc==pc1:
            pc+=1
            cycle+=1
        else:
            pc=pc1
            cycle+=1
        continue
    elif typ=="F":
        type_f(pc)
        break
    printsss(pc)
    pc+=1
    cycle+=1

import matplotlib.pyplot as plt
plt.scatter(xCoordinates, yCoordinates, c="red")
plt.ylabel("Memory Address")
plt.xlabel("Cycle Number")
plt.show()


