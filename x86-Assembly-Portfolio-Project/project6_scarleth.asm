; TITLE Program 6 - Designing Low-Level I/O Procedures   (project6_scarleth.asm)

; Author: Harmony Scarlet
; Last Modified: 3/12/2020
; OSU email address: scarleth@oregonstate.edu
; Course number/section: CS271/400
; Project Number: 6               Due Date: 3/15/2020
; Description: 
;						Program that implements its own REadVal and WriteVal procedures. IT
;						also implements macros getString and displayString. The program tests
;						these procedures and macros by getting 10 integers from the user, 
;						validates the input, and stores the numeric values in an array. The
;						program then displays the integers, their sum, and their average.
;						User input can be positive and/or negative values. 
;
;						Notes: conversion routines use lodsb and stosb operators;  procedure
;						parameters are passed on the system stack; prompts, strings, and other
;						memory locations passed by addres to macros; used registers are saved 
;						and restored by the called preocedures and macros; stack is cleaned up
;						by the called procedure


INCLUDE Irvine32.inc

; MACROS
;------------------------------------------------------------------------------
; getString MACRO - gets a string from the user and stores it in a memory
;										location
; receives: offset of prompt, userString, maxStr, and stringCount
; returns: displays prompt and uses ReadString to store user string in memory
;					 location ideintified by userString, count stored in stringCount loc
; preconditions: None
; registers changed: None
; Postconditions: userString and stringCount stored

getString MACRO prompt, userString, maxStr, stringCount
	pushad

	displayString [prompt]						; display string macro
	mov		edx, [userString]						; userString offset
	mov		ecx, maxStr									; specify max characters
	call	ReadString									; string read and saved to userString/userInput
	mov		ecx, [stringCount]
	mov		[ecx], eax									; number of characters save to inputCount

	popad
ENDM
;------------------------------------------------------------------------------


;------------------------------------------------------------------------------
; displayString MACRO - displays a string using WriteString
; receives: offset of string to display
; returns: displays string
; preconditions: None
; registers changed: None
; Postconditions: None

displayString MACRO output
	push	edx
	mov		edx, [output]
	call	WriteString
	pop		edx
ENDM
;------------------------------------------------------------------------------


ARRAYSIZE = 10

.data
intro1					BYTE		"Designing Low-Level I/O Procedures", 0dh, 0ah
								BYTE		"Programmed by: Harmony Scarlet", 0
introEC					BYTE		"**EC1: Number each line of input and display running subtotal.", 0
intro2					BYTE		"Please provide 10 signed decimal integers.", 0dh, 0ah
								BYTE		"Each number needs to be small enough to fit inside a 32 bit register.", 0dh, 0ah
								BYTE		"After you have finished inputting the raw numbers, I will display a", 0dh, 0ah
								BYTE		"list of the integers, their sum, and their average.", 0
goodbye1				BYTE		"Thank you for participating. Have a great day.", 0
instruct1				BYTE		"Please enter a signed number: ", 0
errorMessage		BYTE		"ERROR: You did not enter a signed number or your number was too big.", 0dh, 0ah
								BYTE		"Please try again.", 0
resultArr				BYTE		"You entered the following numbers:", 0
resultSum				BYTE		"The sum of these numbers is: ", 0
resultAvg				BYTE		"The rounded average is: ", 0
comma						BYTE		",", 0
userInput				BYTE		14 DUP(0)
maxInput				DWORD		13
inputCount			DWORD		?
arrayNums				SDWORD	ARRAYSIZE DUP(?)
userNumber			SDWORD	?	
digitString			BYTE		12 DUP(0)
intSum					SDWORD	?
intAverage			SDWORD	?
spacing					BYTE		" ", 0
subTotalText		BYTE		"Subtotal: ", 0
period					BYTE		".", 0

.code
main PROC

; Introduction
	push	OFFSET intro1
	push	OFFSET introEC
	push	OFFSET intro2
	call	introduction

; Fill Array	
	push	OFFSET period
	push	OFFSET spacing
	push	OFFSET digitString
	push	OFFSET subTotalText
	push	OFFSET arrayNums
	push	ARRAYSIZE
	push	OFFSET userNumber
	push	OFFSET errorMessage
	push	OFFSET instruct1
	push	OFFSET userInput
	push	maxInput
	push	OFFSET inputCount
	call	fillArray

; Sum and Average Calculations
	push	OFFSET intAverage
	push	OFFSET intSum
	push	OFFSET arrayNums
	push	ARRAYSIZE
	call	calculations	

; Display Array
	push	OFFSET spacing
	push	OFFSET resultArr
	push	OFFSET arrayNums
	push	ARRAYSIZE
	push	OFFSET digitString
	push	OFFSET comma
	call	displayArray

; Display Sum and Average
	push	OFFSET resultSum
	push	intSum
	push	OFFSET resultAvg
	push	intAverage
	push	OFFSET digitString
	call	displayResults

; Goodbye
	push	OFFSET goodbye1
	call	goodbye

	exit
main ENDP



;------------------------------------------------------------------------------
; Introduction Procedure - introduces program and displays instructions
; receives: see stack below
; returns: displays introduction and instructions
; preconditions: none
; registers changed: None
; Postconditions: Intro and instructions displayed
; Stack: OFFSET intro1, OFFSET introEC, OFFSET intro2

introduction PROC
	push	ebp
	mov		ebp, esp
	pushad

	displayString [ebp + 16]						; title/programmer
	call	CrLf
	displayString [ebp + 12]						; extra credit intro
	call	CrLf
	call	CrLf
	displayString [ebp + 8]							; instructions
	call	CrLf
	call	CrLf

	popad
	pop		ebp
	ret		12
introduction ENDP
;------------------------------------------------------------------------------



;------------------------------------------------------------------------------
; Fill Array Procedure - fills array with numbers entered by user
; receives: see stack below, recieves input from user as a string 
; returns: displays line number, calls readVal procedure to convert user
;					 entered string to integer and stores all values in arrayNums,
;					 displays running subtotal
; preconditions: subtotal must fit in 32 bit register
; registers changed: None
; Postconditions: array filled
; Stack: OFFSET period, OFFSET spacing, OFFSET digitString, OFFSET subTotalText, 
;				 OFFSET arrayNums, ARRAYSIZE, OFFSET userNumber, OFFSET errorMessage, 
;				 OFFSET instruct1, OFFSET userInput, maxInput, OFFSET inputCount

fillArray PROC
	LOCAL		count:DWORD, subtotal:DWORD
	pushad

	mov		esi, [ebp + 36]								; esi point to empty array
	mov		ecx, [ebp + 32]								; initialize loop counter with arraysize
	mov		count, 1
	mov		subtotal, 0

fill_array_loop:
	; Call ReadVal procedure - get input from User
	push	[ebp + 44]										; @ digitString
	push	count
	push	[ebp + 52]										; @ period
	push	[ebp + 48]										; @ spacing
	push	[ebp + 28]										; @ userNumber
	push	[ebp + 24]										; @ errorMessage
	push	[ebp + 20]										; @ instruct1
	push	[ebp + 16]										; @ userInput
	push	[ebp + 12]										; maxInput
	push	[ebp + 8]											; @ inputCount
	call	readVal												; integer value save to memory location userNumber

	mov		ebx, [ebp + 28]								; point to memory loc of userNumber		
	mov		eax, [ebx]										; mov int value @ ebx to eax	
	mov		[esi], eax										; move integer value to array location @ esi

	; Display subtotal
	displayString [ebp + 40]
	add		subtotal, eax
	push	[ebp + 44]										; OFFSET digitString
	push	subtotal
	call	WriteVal											; convert subtotal to string and display
	call	CrLf
	
	add		esi, 4												; point to next array location
	inc		count
	loop	fill_array_loop
	call	CrLf

	popad
	ret		48
fillArray ENDP
;------------------------------------------------------------------------------



;------------------------------------------------------------------------------
; ReadVal procedure - uses getString macro to get digit string from user and
;											converts the digit string to numeric while validating the
;											user's input
; receives: offset of location to store userNumber, display instruct1, error
;						message, and userInput (string), and maxInput val, all on stack
; returns: userNumber = int value entered by user, inputCount = string count
; preconditions: uses getString macro
; registers changed: None
; Postconditions: user entered string of digits converted to integer
; Stack: 	@ digitString, count, @ period, @ spacing, @ userNumber, 
;				  @ errorMessage, @ instruct1, @ userInput, maxInput, @ inputCount

readVal PROC
	LOCAL	strCount:DWORD, digitSum:SDWORD, signed:BYTE, tempNum:DWORD
	pushad

try_again:

	; Display line number
	push	[ebp + 44]								; OFFSET digitString
	push	[ebp + 40]								; line count	
	call	WriteVal									; converts integer to string and displays string
	displayString [ebp + 36]				; period
	displayString	[ebp + 32]				; display space	

	; use getString macro to get userInput string
	; pass in: OFFSET instruct1, OFFSET userInput, maxInput, OFFSET stringCount
	getString [ebp + 20], [ebp + 16], [ebp + 12], [ebp + 8]

	mov		ebx, [ebp + 8]						; stringCount mem loc
	mov		eax, [ebx]								; move stringCount val to eax
	mov		strCount, eax							; place string count in local variable

	mov		digitSum, 0								; digitSum starts as 0
	mov		signed, 0									; start as 0 (positive)
	cld
	mov		esi, [ebp + 16]						; esi points to userInput String 
	mov		ecx, strCount							; strCount in ecx to track character location
	xor		eax, eax
	lodsb														; load [esi] into eax
	cmp		eax, 43										; + sign entered?
	je		plus_sign
	cmp		eax, 45										; - sign entered?
	je		neg_sign
	jmp		continue									; continue to digit eval if + or - not entered
plus_sign:
	dec		ecx												; if '+' entered in string, dec ecx for next digit
	jmp		next_digit
neg_sign:
	inc		signed										; if '-', change 'signed' to 1 = negative
	dec		ecx												; dec ecx for next digit
next_digit:
	xor		eax, eax
	lodsb														; load [esi] into eax

; Before entering loop, evaluate 1st digit and multiply by -1 if user entered a
; negative number, then enter loop, this allows the use the overflow flag to
; detect if userNum is out of range.
continue:
	cmp		eax, 48										; digit >= 0?
	jl		error_message
	cmp		eax, 57										; digit <= 9?
	jg		error_message
	sub		eax, 48										; subtract 48 from character code to get digit

	mov		tempNum, eax							; digit val in tempNum
	mov		eax, digitSum							; move current digitSum to eax
	xor		edx, edx
	mov		ebx, 10										; digitSum x 10 to move dec place to right
	imul	ebx
	add		eax, tempNum							; add digit
	cmp		signed, 1									; evaluate for negative number
	jne		skip_neg
	mov		ebx, -1							
	imul	ebx												; multiply digitSum by -1 if neg number entered
skip_neg:
	mov		digitSum, eax							; save running total in digitSum
	dec		ecx
	cmp		ecx, 0										; if ecx 0, all digits accounted for
	je		finish

L1:
	xor		eax, eax
	lodsb
	cmp		eax, 48										; digit >= 0?
	jl		error_message
	cmp		eax, 57										; digit <= 9?
	jg		error_message
	sub		eax, 48										; subtract 48 from character code to get digit

	mov		tempNum, eax							; digit val in tempNum
	mov		eax, digitSum
	xor		edx, edx
	mov		ebx, 10
	imul	ebx												; digitSum x 10 to move dec place to right
	jo		error_message							; if overflow, jump to error message

	cmp		signed, 1									; if negative, jump to subtract
	je		subtract

	add		eax, tempNum							; if positive, add tempNum
	jo		error_message							; if overflow flag, num is out of range
	jmp		continue_L1
subtract:
	sub		eax, tempNum							; if negative, subtract tempNum
	jo		error_message							; if overflow flag, num is out of range
continue_L1:
	mov		digitSum, eax							; update digitSum variable to new value
	loop	L1
	jmp		finish

error_message:
	displayString [ebp + 24]				; use macro to display error message
	call	CrLf
	jmp		try_again

finish:
	mov		ebx, [ebp + 28]						; move memory location for userNumber
	mov		[ebx], eax								; save final digitSum to userNumber
	popad
	ret		40
readVal	ENDP
;-----------------------------------------------------------------------------;



;-----------------------------------------------------------------------------;
; calculations procedure: sums the numbers in an array then calculates average
; Receives: intSum offset, array offset, and ARRAYSIZE on system stack
; Returns: sum of array nums in intSum, average in intAverage
; Preconditions: array contains numbers, may be positive or negative or both
; Registers changed: None
; Postconditions: array sum in intSum, average in intAverage
; Stack: OFFSET intAverage, OFFSET intSum, OFFSET arrayNums, ARRAYSIZE

calculations PROC
	pushad
	mov		ebp, esp

	mov		ecx, [ebp + 36]						; set up loop counter
	mov		esi, [ebp + 40]						; point to beginning of array
	mov		eax, 0

sum_loop:
	add		eax, [esi]
	add		esi, 4
	loop	sum_loop

	mov		edx, [ebp + 44]
	mov		[edx], eax								; save sum to intSum

	cdq															; extend sign of eax into edx
	mov		ebx, [ebp + 36]						; move arraysize to ebx
	idiv	ebx												; sum / arraysize

	mov		edx, [ebp + 48]
	mov		[edx], eax								; save average to intAverage

	popad
	ret	16
calculations ENDP
;-----------------------------------------------------------------------------;



;------------------------------------------------------------------------------
; WriteVal procedure - converts a numeric value to a digit string and uses
;											 displayString macro to display the string 
; receives: numeric value on stack, offset of digit string
; returns: displays digit string
; preconditions: signed integer value can be stored in 32 bit register, uses
;								 displayString macro
; registers changed: None
; Postconditions: memory location of digitString contains values of digit string
; Stack: OFFSET digitString, value to display

writeVal PROC
	LOCAL		numericVal:DWORD, signed:BYTE, quotient:DWORD, ptrString:DWORD
	pushad
	
	mov		edi, [ebp + 12]						; point to digit string
	add		edi, 11										; point to last byte
	mov		eax, 0										; insert null byte
	std
	stosb

	mov		ecx, 10										; max digits is 10 to fit in 32 bit register
	mov		eax, [ebp + 8]						; move numeric val to eax
	mov		numericVal, eax						; save numeric val as local variable
	cmp		numericVal, 0
	jge		not_negative							; signed = 1 local variable if negative
	mov		signed, 1
	mov		ebx, -1
	imul	ebx												; if negative, make positive
not_negative:

write_loop:
	mov		ebx, 10								
	xor		edx, edx
	div		ebx												; div int/10 = quotient in eax, remainder in edx
	mov		quotient, eax							; save quotient as local variable 'quotient'
	mov		eax, edx									; remainder is digit to store at byte location
	add		eax, 48										; add 48 to get character code
	std
	stosb														; store value in al at location pointed to [edi], dec edi

	cmp		quotient, 0								; if quotient is 0, all digits have been saved to string
	je		eval_sign
	mov		eax, quotient							; move quotient to eax to evaluate next digit
	loop	write_loop

eval_sign:
	cmp		signed, 0
	je		display_num								; if positive, jump to display_num
	mov		eax, 45										; add '-' sto string if negative number
	std
	stosb														; store value in al ('-') at location pointed to [edi]

display_num:
	inc		edi												; inc edi to point to start of string
	mov		ptrString, edi						; save memory location to ptrString
	displayString ptrString					; call displayString macro

	popad
	ret		8
writeVal ENDP
;-----------------------------------------------------------------------------;



;------------------------------------------------------------------------------
; Display array procedure - displays array
; receives: offsets of resultArr text, array, digitString, comma, ARRAYSIZE val
;						all on stack
; returns: displays string, displays array by calling writeVal proc
; preconditions: arrayNums is an array of integers
; registers changed: None
; Postconditions: array displayed
; Stack: OFFSET spacing, OFFSET resultArr, OFFSET arrayNums, ARRAYSIZE,
;				 OFFSET digitString, OFFSET comma

displayArray PROC
	push	ebp
	mov		ebp, esp
	pushad

	displayString [ebp + 24]				; display title text
	call	CrLf

	mov		esi, [ebp + 20]						; point esi to start of array
	mov		ecx, [ebp + 16]						; initialize loop counter with arraysize
	dec		ecx												; minus one to print last integer without comma

display_loop:
	mov		eax, [esi]								; integer value in array @ esi to eax
	push	[ebp + 12]								; point to memory location of empty string
	push	eax												; push integer value from array onto stack
	call	writeVal									; converts integer to string and displays string
	displayString [ebp + 8]					; comma
	displayString [ebp + 28]				; spacing
	add		esi, 4										; point to next array value
	loop	display_loop
	
	mov		eax, [esi]								; display final number without comma
	push	[ebp + 12]								; point to memory location of empty string
	push	eax												; push numeric value from array onto stack
	call	writeVal									; converts integer to string and displays string
	call	CrLf

	popad
	pop		ebp
	ret		24
displayArray ENDP
;-----------------------------------------------------------------------------;



;------------------------------------------------------------------------------
; Display results procedure - displays sum and average results
; receives: offsets of result strings and sum and avarage values on stack
; returns: displays string, displays result values by calling writeVal proc
; preconditions: sum and average are integer values
; registers changed: None
; Postconditions: results displayed
; Stack: OFFSET resultSum, intSum, OFFSET resultAvg, intAverage, OFFSET digitString

displayResults PROC
	push	ebp
	mov		ebp, esp 
	pushad

	; Display Sum
	displayString [ebp + 24]				; display sum result title
	push	[ebp + 8]									; OFFSET digitString
	push	[ebp + 20]								; intSum
	call	WriteVal									; converts integer to string and displays string
	call	CrLf

; Display Average
	displayString [ebp + 16]				; display average result title
	push	[ebp + 8]									; OFFSET digitString
	push	[ebp + 12]								; intAverage
	call	WriteVal									; converts integer to string and displays string
	call	CrLf
	call	CrLf

	popad
	pop		ebp
	ret		20
displayResults ENDP
;-----------------------------------------------------------------------------;


;------------------------------------------------------------------------------
; Goodbye Procedure - displays goodbye message
; receives: OFFSET goodbye1
; returns: displays parting message
; preconditions: none
; registers changed: None
; Postconditions: displays parting message
; Stack: OFFSET goodbye1

goodbye PROC
	push	ebp
	mov		ebp, esp
	pushad

	displayString [ebp + 8]
	call	CrLf

	popad
	pop		ebp
	ret		4

goodbye ENDP
;------------------------------------------------------------------------------

END main
