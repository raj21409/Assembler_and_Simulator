import sys

asm=[]
for line in sys.stdin:
    asm.append(line)   
# f=open("code1.txt",'r')
# for line in f:
#     asm.append(line) 
# print(asm)
machinecode=[]
def opcode(op,chk):
    opcodes={
        "add":"10000",
        "sub":"10001",
        "ld" :"10100",
        "st" :"10101",
        "mul":"10110",
        "div":"10111",
        "rs" :"11000",
        "ls" :"11001",
        "xor":"11010",
        "or" :"11011",
        "and":"11100",
        "not":"11101",
        "cmp":"11110",
        "jmp":"11111",
        "jlt":"01100",
        "jgt":"01101",
        "je" :"01111",
        "hlt":"01010",
        "addf":"00000",
        "subf":"00001",
        "movf":"00010",
        "mov":["10010","10011"] #imm and reg
        }
    if op=='mov' and chk=="R":
        return opcodes[op][1]
    elif op=='mov' and chk=="I":
        return opcodes[op][0]
    else:
        return opcodes[op]

def instr_type(op,noofreg=0):
    type={
        'A':["add","sub","mul","xor","or","and","addf","subf"],
        'B':["mov","rs","ls","movf"],
        'C':["mov","div","not","cmp"],
        'D':["ld","st"],
        'E':["jmp","jlt","jgt","je"],
        'F':["hlt"]
        }
    # for t in type:
    #     if op in type[t]:
    #         return t

    if noofreg==1:
        return 'B'
    elif noofreg==2:
        return 'C'
    else:
        for t in type:
            if op in type[t]:
                return t
    
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
    return ans
def regaddress(reg):
    registers = {
        'R0'  :'000',
        'R1'  :'001',
        'R2'  :'010',
        'R3'  :'011',
        'R4'  :'100',
        'R5'  :'101',
        'R6'  :'110',
        'FLAGS':'111'}
    if reg in registers:
        return registers[reg]
    else:
        return -1
def to8bit(num):
     x='{:08b}'.format(num)
     return str(x)

variables=dict()
labels=dict()
errors=[]
# Removing Empty Lines
for line in asm:
    if(line=="\n"):
        asm.remove(line)
        

# Counting variables:
no_ofvar=0
for line in asm:
    if(line.split()[0]=="var"):
        no_ofvar+=1
    else:
        break
# Variable Declaration:
variable_Addr=len(asm)-no_ofvar

def float_bin(my_number, places = 3):
    my_whole, my_dec = str(my_number).split(".")
    my_whole = int(my_whole)
    res = (str(bin(my_whole))+".").replace('0b','')
 
    for x in range(places):
        my_dec = str('0.')+str(my_dec)
        temp = '%1.20f' %(float(my_dec)*2)
        my_whole, my_dec = temp.split(".")
        res += my_whole
    return res

for line in asm:
    bline=line.split()
    if(bline[0]=="var"):
        variables[bline[1]]=to8bit(variable_Addr)
        variable_Addr+=1
    else:
        break
for linenum in range(len(asm)):
    asm[linenum]=asm[linenum].rstrip()
    # print(line)
# print(asm)


def mant(n) :
    if n < 0 :
        
        n = n * (-1)
    p = 30

    dec = float_bin (n, places = p)
 
    d = dec.find('.')
    onePlace = dec.find('1')
    # finding the mantissa
    if onePlace > d:
        dec = dec.replace(".","")
        onePlace -= 1
        d -= 1
    elif onePlace < d:
        dec = dec.replace(".","")
        d -= 1
    mantissa = dec[onePlace+1:]
    return mantissa
# Removing Variables for Instruction Index:
for i in range(no_ofvar):
    del asm[0]

# Label Declaration
line_no=0
for line in asm:
    if line=="":
        asm.remove(line)
        continue
    bline=line.split()
    if(bline[0][-1]==":"):
        if (bline[0][:len(bline[0]):1] not in labels):
            labels[bline[0][:len(bline[0])-1:1]]=to8bit(line_no)
        rem=[]
        i=1
        while(i<len(bline)):
            rem.append(bline[i])
            i+=1
        remst=" ".join(rem)
        asm[line_no]=remst
    line_no+=1
# cleaning of data:
# print(labels)
for lineno in range(len(asm)):
    asm[lineno]=asm[lineno].strip()
# print(asm)
haltflag=0
#----------------
no_oflines=len(asm)
for lineptr in range(no_oflines):
    if asm[lineptr]=="":
            errors.append("ERROR : Syntax Error at lineno. --> "+ str(lineptr))
            continue
    brline=asm[lineptr].split()
    if brline[0]=='var':
            errors.append("ERROR : Variable not declared at the beginning at lineno. --> "+ str(lineptr))
            continue
    if brline[0]=='hlt' and lineptr!=no_oflines-1:
            haltflag=1
            errors.append("ERROR : halt not used as last instruction at lineno. --> "+ str(lineptr))
            continue
    if brline[0] not in ("add","sub","mov","ld" ,"st" ,"mul","div", "rs" , "ls" , "xor", "or" ,"and","not","cmp","jmp","jlt","jgt","je","hlt","movf","addf","subf"):
         errors.append("ERROR : typo in  instruction at lineno. --> "+ str(lineptr))
         continue

 #-------------------------------------------'A':["add","sub","mul","xor","or","and","addf","subf"]------------------------------------------------------------------
    elif instr_type(brline[0])=='A':
           if len(brline)!=4:
                errors.append("ERROR: Syntax Error(L) at lineno. --> "+ str(lineptr))
                continue
           first=regaddress(brline[1])
           second=regaddress(brline[2])
           third=regaddress(brline[3])
           if first==-1 or second==-1 or third==-1:
                errors.append("ERROR: Undefined Register at lineno. --> "+ str(lineptr))
                continue
           if first=="111" or second=="111" or third=="111":
                errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                continue

           machinecode.append(opcode(brline[0],'DC')+"00"+first+second+third)
           continue
#  --------------------------------------------------------------'B':["mov","rs","ls","movf"]------------------------------------------------------------------
    elif instr_type(brline[0])=='B':
          if len(brline)!=3:
            errors.append("ERROR: Syntax Error(L) at lineno. --> "+ str(lineptr))
            continue
          if brline[0]=='mov':
                if brline[2][0]=='$':
                    first=regaddress(brline[1])
                    if first==-1:
                        errors.append("ERROR : Undefined Register at lineno. --> "+ str(lineptr))
                        continue
                    if first=="111":
                        errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                        continue
                    imm=int(brline[2][1::])
                    if imm not in range(0,256):
                        errors.append("ERROR: illegal immediate value at lineno. --> "+ str(lineptr))
                        continue
                    machinecode.append(opcode('mov','I')+first+to8bit(imm)) 
                    
                    
                    
                else:                  
                    first=regaddress(brline[1])
                    second=regaddress(brline[2])
                    if first==-1 or second==-1:
                        errors.append("ERROR: Undefined Register at lineno. --> "+ str(lineptr))
                        continue
                    if second=="111":
                        errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                        continue
                    machinecode.append(opcode('mov','R')+"00000"+first+second)
                    continue     
          elif brline[0]=='movf':

                if brline[2][0]=='$':
                    first=regaddress(brline[1])
                    if first==-1:
                        errors.append("ERROR : Undefined Register at lineno. --> "+ str(lineptr))
                        continue
                    if first=="111":
                        errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                        continue
                    imm=float(brline[2][1::])
                    fc=0
                    man=mant(imm)
                    for i in man[5:]:
                         if i=="1":
                             fc=1
                    if fc==1:
                        errors.append("ERROR: illegal immediate value at lineno. --> "+ str(lineptr))
                        continue
                    machinecode.append(opcode('movf','DC')+first+floattoieee(imm))
              
          else:
            first=regaddress(brline[1])
            imm=int(brline[2][1::])
            if first==-1:
                errors.append("ERROR: Undefined Register at lineno. --> "+ str(lineptr))
                continue
            if first=="111":
                errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                continue
            if imm not in range(0,256):
                errors.append("ERROR: illegal immediate value at lineno. --> "+ str(lineptr))
                continue
            machinecode.append(opcode(brline[0],'DC')+first+to8bit(imm))
            continue
# --------------------------------------------------------------'C':["mov","div","not","cmp"]-----------------------------------------------------------
    elif instr_type(brline[0])=='C':
          if len(brline)!=3:
            errors.append("ERROR: Syntax Error(L) at lineno. --> "+ str(lineptr))
            continue
          if brline[0]=='mov':
                if brline[2][0]=='$':
                    first=regaddress(brline[1])
                    if first==-1:
                        errors.append("ERROR : Undefined Register at lineno. --> "+ str(lineptr))
                        continue
                    if first=="111":
                        errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                        continue
                    imm=int(brline[2][1::])
                    if imm not in range(0,256):
                        errors.append("ERROR: illegal immediate value at lineno. --> "+ str(lineptr))
                        continue
                    machinecode.append(opcode('mov','I')+first+to8bit(imm)) 
                    
                    
                    
                else:                  
                    first=regaddress(brline[1])
                    second=regaddress(brline[2])
                    if first==-1 or second==-1:
                        errors.append("ERROR: Undefined Register at lineno. --> "+ str(lineptr))
                        continue
                    if second=="111":
                        errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                        continue
                    machinecode.append(opcode('mov','R')+"00000"+first+second)
                    continue
          else:
            first=regaddress(brline[1])
            second=regaddress(brline[2])
            if first==-1 or second==-1:
                errors.append("ERROR: Undefined Register at lineno. --> "+ str(lineptr))
                continue
            if first=="111" or second=="111":
                errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
                continue
            machinecode.append(opcode(brline[0],'DC')+"00000"+first+second)
            continue
# --------------------------------------------------------------'D':["ld","st"]-------------------------------------------------------------------------
    elif instr_type(brline[0])=='D':
          if len(brline)!=3:
            errors.append("ERROR: Syntax Error(L) at lineno. --> "+ str(lineptr))
            continue
          first=regaddress(brline[1])
          if first==-1:
            errors.append("ERROR: Undefined Register at lineno. --> "+ str(lineptr))
            continue
          if first=="111":
            errors.append("ERROR: illegal use of flag at lineno. --> "+ str(lineptr))
            continue
          if brline[2] in labels and brline[2] not in variables:
               errors.append("ERROR: Misuse of lable as variable at lineno. --> "+ str(lineptr))
               continue
          elif brline[2] not in variables:
               errors.append("ERROR: Undefined variables at lineno. --> "+ str(lineptr))
               continue
          machinecode.append(opcode(brline[0],'DC')+first+variables[brline[2]])
          continue
#--------------------------------------------------------------'E':["jmp","jlt","jgt","je"]-------------------------------------------------------------------
    elif instr_type(brline[0])=='E':
           if len(brline)!=2:
            errors.append("ERROR: Syntax Error(L) at lineno. --> "+ str(lineptr))
            continue
           if brline[1] in variables and brline[1] not in labels:
               errors.append("ERROR: Misuse of variable as label at lineno. --> "+ str(lineptr))
               continue
           elif brline[1] not in labels:
               errors.append("ERROR: Undefined label at lineno. --> "+ str(lineptr))
               continue
           machinecode.append(opcode(brline[0],'DC') +"000"+labels[brline[1]])
           continue 

#--------------------------------------------------------------'F':["hlt"]----------------------------------------------------------------------------------

    elif instr_type(brline[0])=='F':
          if len(brline)!=1:
            errors.append("ERROR: Syntax Error(L) at lineno. --> "+ str(lineptr))
            continue
          machinecode.append(opcode(brline[0],'DC')+"00000000000")
          haltflag=1
          continue
    else:
        errors.append("ERROR : Syntax Error at lineno. --> "+ str(lineptr))
        continue
if haltflag !=1:
    errors.append("ERROR: halt missing.")
if len(machinecode)<=256:
    for line in machinecode:
        print(line)
else:
    errors.append("ERROR: more than 256 lines")

#***********************************************************************__ERROR__******************************************************************************************

for er in errors:
        print(er)
        # break

        


      