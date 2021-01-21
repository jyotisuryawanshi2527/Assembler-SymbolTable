section data
	var1 db 'abcd efgh' ,10 , "asd", 255,0
	var2 db 'abc def ghi jkl',10,0
	var3 db 0
	var4 dd ''
	var5 dd 'abc'
	var6 dd "abcde"
	var7 dd 'abcde',10
	var8 dd 'abc',10,'ab'

section .text
	global main
main:
l1:	mov eax, var8
	mov eax, 10
	mov edi, 12345
	jmp l5
	mov eax, dword[var1]
	mov eax, dword[123]

l2:	add ebx, var7
	add eax, 10
	add ecx, 10
	add edi, 12345
	jmp l5
	add ecx, dword[var2]
	add eax, dword[123]

l3:	sub ebx, var6
	sub ecx, 10
	jmp l3
	sub edi, 12345
	sub ecx, dword[var3]
	sub eax, dword[123]

l4:	jmp l1
	cmp ebx, var5
	cmp ecx, 10
	cmp edi, 12345
	cmp ecx, dword[var4]
	cmp eax, dword[123]

l5:	mul eax
	mul edi
	mul dword[var5]
	mul dword[123]
	jmp l3

	div eax
	div edi
	div dword[var5]
	div dword[123]

	int 80h

