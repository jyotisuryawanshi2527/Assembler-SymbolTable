
import sys
from sys import argv

def isValidVar(str1):
	alphabatestr = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	numberstr = '0123456789'
	validvar = -1
	for x in str1:
		if x in alphabatestr+numberstr+'_'+'.':
			validvar = 0
		else:
			validvar = 1
			break;
	if str1[0][:1] not in alphabatestr+'_'+'.':
		validvar = 1
	return validvar



#main code

sourceFile = open("sourceFile1.asm")
symbolTableFile = open("outputSymbTable.s", "w")
splitFile = []
splitFile1 = []

keywordTable = ['eax','ecx','edx','ebx','esp','ebp','esi','edi', '.data','.text','dd','db','resd','var','label']
opcodeTable = ['mov','add','sub','mul','div','cmp','jmp','int']
regesterTable = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
symbolTable = [] #id,name,type,address,d/u,size
errorTable = (open("asmErrorTable.txt")).read().split('\n')
literalTable = [] #int,hex
printErrors = []
finalHex = []

for line in sourceFile:
	line = line.replace('\n', '')
	splitFile.append(line)

#print(splitFile)
#print("\n")
#for ele in errorTable:
#	print(ele)
#print("\n")

temp = ''
linenum = 0
for ele in splitFile: #make list of lines ie formated source code
	linenum += 1
	temp = str(linenum)+' '+ele
	temp = temp.replace('\t', '')
	temp = temp.replace(',', ' , ')
	temp = temp.replace(';', ' ; ')
	temp = temp.replace(':', ' : ')
	temp = temp.replace('"', '\'')
	temp = temp.replace('\'', '\'@\'')

	temp = temp.split('\'')
	temp2 = []
	temp3 = []
	flag = 0
	for ele1 in temp:
		if ele1 == '@' and flag == 0:
			flag = 1
			continue
		elif ele1 == '@' and flag == 1:
			flag = 0
			continue

		if flag == 0:
			temp2.append(ele1.split(' '))
		elif flag == 1:
			temp2.append(['\''+ele1+'\''])
		
	for ele1 in temp2:
		temp3 = temp3+ele1
	while '' in temp3:
		temp3.remove('')


	flag = 0
	temp4 = []
	for ele1 in temp3:
		if ele1 == ';': #remove comments
			temp3 = temp3[:temp3.index(ele1)]
		if ele1 == ':': #take label on seperate line
			temp4 = temp3[3:] #[delete:keep] first k ele
			temp4.insert(0, str(linenum))
			temp3 = temp3[:3]
			temp3 = [temp3[0], temp3[1]+temp3[2]]
			flag = 1

	splitFile1.append(temp3)
	if flag == 1 and len(temp4) > 1:
		splitFile1.append(temp4)

#for ele in splitFile1:
#	print(ele)

############################################################################


symbolTableid = 0
address = 0
for lineIndex, inst in enumerate(splitFile1): #read line by line for error/symbol table
	bytes = 0 
	byteinc = 0 
	variableflag = 0 #variable declaration found then proceed

	if len(inst) < 2:
		continue
	elif inst[1] == 'section' or inst[1] == 'global':
		if len(inst) == 2:
			#WAR-macro exists, but not taking 0 parameters
			printErrors.append(inst[0])
			printErrors.append(1)
			continue
		elif len(inst) == 3:
			validvar = isValidVar(inst[2])
			if validvar == 0 and inst[1] == 'section':
				address = 0;
			elif validvar == 0:
				#inst[2] inserts into SYMBOLTABLE with U
				#search label in symbol table, if already found
				#WAR-GLOBAL directive after symbol definition is
				#an experimental feature
				if inst[2] in symbolTable:
					printErrors.append(inst[0])
					printErrors.append(12)
					continue
				else:
					symbolTable.append(inst[0])
					symbolTable.append(inst[2])
					symbolTable.append('label')
					symbolTable.append(0)
					symbolTable.append('U')
					symbolTable.append(0)
					continue	
			else:
				#ERR-identifier expected after macro
				printErrors.append(inst[0])
				printErrors.append(2)
				continue
		else:
			if inst[1] == 'section':
				#ERR-Unknown section attribute ignored
				printErrors.append(inst[0])
				printErrors.append(3)
				continue
			elif inst[1] == 'global':
				#ERR-macro global have many parameters
				printErrors.append(inst[0])
				printErrors.append(4)
				continue


	elif inst[1] in opcodeTable:
		opflag = 1		
		if len(inst) == 3:
			if inst[1] == 'jmp':
				if inst[2] in keywordTable+opcodeTable:
					#ERR:invalid combination of opcode and operands
					opflag = 10
				else:
					address = address+2
					opflag = 2
			elif inst[1] == 'int':
				if inst[2] in keywordTable+opcodeTable or inst[2] != '80h':
					#ERR:invalid combination of opcode and operands
					opflag = 10
				else:
					address = address+2
					#opflag = 2
			else:
				if inst[2] in regesterTable:
					address = address+2
				elif inst[2].startswith('dword[') and inst[2].endswith(']'):
					address = address+6
					str1 = inst[2][6:]
					str1 = str1[:len(str1)-1]
					if str1.isdigit():
						if int(str1) > 4294967295:
							#WAR-dword data exceeds bounds
							printErrors.append(inst[0])
							printErrors.append(16)
						continue
					else:
						if str1 not in symbolTable:
							#ERR-unexpected format of dword[imm/var]
							printErrors.append(inst[0])
							printErrors.append(17)
							continue
				else:
					#ERR:invalid combination of opcode and operands
					opflag = 10
		elif len(inst) == 5:
			if inst[3] != ',':
				#ERR-comma expected
				printErrors.append(inst[0])
				printErrors.append(10)
				continue
			elif inst[2] not in regesterTable:
				#ERR:invalid combination of opcode and operands
				opflag = 10
			else:
				if inst[4] in regesterTable:#opcode reg, reg
					address = address+2
				elif inst[4].startswith('dword[') and inst[4].endswith(']'):
					if inst[1] == 'mov' and inst[2] == 'eax':
						address = address+5
					else:
						address = address+6
					str1 = inst[4][6:]
					str1 = str1[:len(str1)-1]
					if str1.isdigit():
						if int(str1) > 4294967295:
							#WAR-dword data exceeds bounds
							printErrors.append(inst[0])
							printErrors.append(16)
							continue
					else:
						if str1 not in symbolTable:
							#ERR-unexpected format of dword[imm/var]
							printErrors.append(inst[0])
							printErrors.append(17)
							continue		
				else: #opcode reg, imm/var
					if inst[1] == 'mov':
						address = address+5
					else:
						if inst[4].isdigit():
							if int(inst[4]) > 255:
								address = address+6
							else: 
								address = address+3
						else: #opcode reg, imm
							address = address+6

					if inst[4].isdigit():
						if int(inst[4]) > 4294967295:
							#WAR-dword data exceeds bounds
							printErrors.append(inst[0])
							printErrors.append(16)
							continue
					else:
						validvar = isValidVar(inst[opflag])
						if validvar == 0:
							opflag = 4
						else:
							#ERR-unexpected label/variable name
							printErrors.append(inst[0])
							printErrors.append(7)
							continue
		else:
			#ERR:invalid combination of opcode and operands
			opflag = 10


		if opflag != 1 and opflag != 10:
			validvar = isValidVar(inst[opflag])
			if validvar == 0:
				if inst[opflag] not in symbolTable:
					symbolTable.append(inst[0])
					symbolTable.append(inst[opflag])
					if opflag == 2:
						symbolTable.append('label')
					elif opflag == 4:
						symbolTable.append('var')
					symbolTable.append(0)
					symbolTable.append('U')
					symbolTable.append(0)
					continue
			else:
				#ERR-unexpected label/variable name
				printErrors.append(inst[0])
				printErrors.append(7)
				continue
		elif opflag == 10:
			#ERR:invalid combination of opcode and operands
			printErrors.append(inst[0])
			printErrors.append(13)
			continue


	else: #label/variable
		labelflag = 0
		if inst[1].endswith(':'):
			labelflag = 1
			inst[1] = inst[1][:len(inst[1])-1]

		if inst[1] in keywordTable:
			#ERR-label or variable expected at start of line
			printErrors.append(inst[0])
			printErrors.append(5)
			continue

		validvar = isValidVar(inst[1])
		if validvar == 0:
			if inst[1] in symbolTable:
				if symbolTable[symbolTable.index(inst[1])+3] == 'D':
					printErrors.append(inst[0])
					str1 = 'symbol \''+inst[1]+'\' is redefined'
					printErrors.append(str1)
					continue
			if len(inst) == 2:
				if labelflag == 1:
					#inst[1] inserts into SYMBOLTABLE with D
					#search label in symbol table, if found 
					#find index and replace data
					if inst[1] in symbolTable:
						index = symbolTable.index(inst[1])
						symbolTable[index+2] = address
						symbolTable[index+3] = 'D'
					else:
						symbolTable.append(inst[0])
						symbolTable.append(inst[1])
						symbolTable.append('label')
						symbolTable.append(address)
						symbolTable.append('D')
						symbolTable.append(0)
						continue
				else:
					#ERR-label without column
					printErrors.append(inst[1])
					printErrors.append(6)
					continue
			elif len(inst) > 2 and (inst[2]=='db' or inst[2]=='dd' or inst[2]=='resd'):
				variableflag = 1
			else:
				#ERR-label without column
				printErrors.append(inst[0])
				printErrors.append(6)
				continue
		else:
			#ERR-unexpected label/variable name
			printErrors.append(inst[0])
			printErrors.append(7)
			continue


	if variableflag == 1:
		if len(inst) == 3:
			#ERR-no operand for data declaration
			printErrors.append(inst[0])
			printErrors.append(9)
			continue
		if inst[2] == 'db':
			byteinc = 1
		elif inst[2] == 'dd':
			byteinc = 4
		symbolTable.append(inst[0])
		symbolTable.append(inst[1])
		symbolTable.append('var')
		symbolTable.append(address)
		symbolTable.append('D')

		for x in range(3, len(inst)):
			if x%2 == 0 and inst[x] != ',':
				#ERR-comma expected
				printErrors.append(inst[0])
				printErrors.append(10)
				break
			elif x%2 != 0:
				if inst[x].isdigit():
					if inst[2] == 'db' and int(inst[x]) > 255:
						#WAR-byte data exceeds bounds
						printErrors.append(inst[0])
						printErrors.append(15)
						continue
					if inst[2] == 'dd' and int(inst[x]) > 4294967295:
						#WAR-dword data exceeds bounds
						printErrors.append(inst[0])
						printErrors.append(16)
						continue

					bytes += byteinc
				elif inst[x].startswith('\'') and inst[x].endswith('\''):
					if len(inst[x]) > 2:
						t1 = int((len(inst[x])-2-1)/byteinc)+1
						bytes = bytes+(t1*byteinc)
				elif type(inst[x]) == str:
					#ERR-reserve non-constant quantity in declaration
					printErrors.append(inst[0])
					printErrors.append(14)
					break
				else:
					#ERR-expression syntex error
					printErrors.append(inst[0])
					printErrors.append(11)
					break
		symbolTable.append(bytes)
		address = address+bytes


#insert errors from symbol table
print("\n")
for ind, ele in enumerate(symbolTable):
	if ele == 'U':
		printErrors.append(str(symbolTable[ind-4]))
		str1 = "symbol "+symbolTable[ind-3]+" is undefined"
		printErrors.append(str1)

###############################################################################
#print("\n")
#print(printErrors)
#print("\n")
for ind, ele in enumerate(printErrors):
	if ind%2 == 0:
		if type(printErrors[ind+1]) != str:
			print(argv[0]+':',' '*(2-len(ele))+ele+':',errorTable[2*(printErrors[ind+1])-1])
		else:
			print(argv[0]+':',' '*(2-len(ele))+ele+':', printErrors[ind+1])





if len(printErrors) != 0:
	sys.exit(0)
else:
	###############################################################################
	print("Symbol Table:\n")
	symbolTable1 = []
	str1 = ''
	str1 = '    LINE'+'    NAME'+'    TYPE'+'    ADDR'+'     D/U'+'    SIZE'
	symbolTable1.append(str1)
	for ind, ele in enumerate(symbolTable):
		str1 = ''
		if ind%6 == 0:
			str1 = str1+' '*(8-len(str(symbolTable[ind+0])))+symbolTable[ind+0]
			str1 = str1+' '*(8-len(symbolTable[ind+1]))+symbolTable[ind+1]
			str1 = str1+' '*(8-len(symbolTable[ind+2]))+symbolTable[ind+2]
			str1 = str1+' '*(8-len(str(symbolTable[ind+3])))+str(symbolTable[ind+3])
			str1 = str1+' '*(8-len(str(symbolTable[ind+4])))+symbolTable[ind+4]
			str1 = str1+' '*(8-len(str(symbolTable[ind+5])))+str(symbolTable[ind+5])
			symbolTable1.append(str1)

	for ele in symbolTable1:
		symbolTableFile.write(ele)
		symbolTableFile.write('\n')
		print(ele)
	###############################################################################




