#!/usr/bin/env python2.7

import sys, io
import struct

class VM:
	def __init__(self):
		self.MAX_INT = 32768
		
		# eight self.registers, from 0 to 7
		self.registers = [0 for x in range(8)]
		
		# unbounded self.stack
		self.stack = []
		
		self.tracking = False;
		
		self.inputHandler = None
	
		self.location = 0
		
		# total number of arguments by op command
		self.increment = {0:1,1:3,2:2,3:2,4:4,5:4,6:2,7:3,8:3,9:4,10:4,11:4,
						  12:4,13:4,14:3,15:3,16:3,17:2,18:1,19:2,20:2,21:1}
		
		# Read input file into self.memory.
		self.memory = []
	
	# returns either the literal value or the appropriate elt from self.registers
	def getValue(self, i):
		assert i < self.MAX_INT+8 # invalid numbers
		if i < self.MAX_INT: # return literal
			return i
		else: # return val from self.registers
			return self.registers[i%self.MAX_INT]

	def mainLoop(self):
		while True:
			nextCmd = self.memory[self.location]
			
			# trying to extract the algorithm:
			if self.tracking:
				inc = self.increment[nextCmd]
				for i in range(self.location,self.location+inc+1):
					print self.memory[i],
				print ""
			
			if nextCmd == 0: # halt
				'''stop execution and terminate the program'''
				sys.exit()
			
			elif nextCmd == 1: # set
				'''set register <a> to the value of <b>'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				self.registers[a] = b
				self.location += 3
				
			elif nextCmd == 2: # push
				'''push <a> onto the self.stack'''
				a = self.getValue(self.memory[self.location+1])
				self.stack.append(a)
				self.location += 2
				
			elif nextCmd == 3: # pop
				'''remove the top element from the self.stack and write it into <a>; empty self.stack = error'''
				try:
					# we can just use list.pop() too
					self.registers[self.memory[self.location+1]%32768] = self.stack[-1]
					self.stack = self.stack[:-1]
				except:
					print("Empty self.stack; cannot pop")
				self.location += 2
				
			elif nextCmd == 4: # eq
				'''set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				c = self.getValue(self.memory[self.location+3])
				
				if b==c: self.registers[a] = 1
				else: self.registers[a] = 0

				self.location += 4
				
			elif nextCmd == 5: # gt
				'''set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				c = self.getValue(self.memory[self.location+3])
				
				if b>c: self.registers[a] = 1
				else: self.registers[a] = 0

				self.location += 4
				
			elif nextCmd == 6: # jmp
				'''jump to <a>'''
				a = self.getValue(self.memory[self.location+1])
				self.location = a
				
			elif nextCmd == 7: # jt
				'''if <a> is nonzero, jump to <b>'''
				a = self.getValue(self.memory[self.location+1])
				b = self.getValue(self.memory[self.location+2])
				
				if a != 0: self.location = b
				else: self.location += 3
					
			elif nextCmd == 8: # jf
				'''if <a> is zero, jump to <b>'''
				a = self.getValue(self.memory[self.location+1])
				b = self.getValue(self.memory[self.location+2])
				
				if a == 0: self.location = b
				else: self.location += 3
					
			elif nextCmd == 9: # add
				'''assign into <a> the sum of <b> and <c> (modulo 32768)'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				c = self.getValue(self.memory[self.location+3])
				
				self.registers[a] = (b+c)%32768
				
				self.location += 4
				
			elif nextCmd == 10: # mult
				'''store into <a> the product of <b> and <c> (modulo 32768)'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				c = self.getValue(self.memory[self.location+3])
			
				self.registers[a] = (b*c)%32768
				
				self.location += 4
				
			elif nextCmd == 11: # mod
				'''store into <a> the remainder of <b> divided by <c>'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				c = self.getValue(self.memory[self.location+3])
				
				self.registers[a] = (b%c)
				
				self.location += 4
				
			elif nextCmd == 12: # and
				'''stores into <a> the bitwise and of <b> and <c>'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				c = self.getValue(self.memory[self.location+3])
				
				self.registers[a] = (b&c)
				
				self.location += 4
				
			elif nextCmd == 13: # or
				'''stores into <a> the bitwise or of <b> and <c>'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				c = self.getValue(self.memory[self.location+3])
				
				self.registers[a] = (b|c)
				
				self.location += 4
				
			elif nextCmd == 14: # not
				'''stores 15-bit bitwise inverse of <b> in <a>'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				
				self.registers[a] = b^32767 # produces the 15-bit bitwise inverse of b
						
				self.location += 3
				
			elif nextCmd == 15: # rmem
				'''read self.memory at address <b> and write it to <a>'''
				a = self.memory[self.location+1]%32768
				b = self.getValue(self.memory[self.location+2])
				self.registers[a] = self.memory[b]
				self.location += 3
				
			elif nextCmd == 16: # wmem
				'''write the value from <b> into self.memory at address <a>'''
				a = self.getValue(self.memory[self.location+1])
				b = self.getValue(self.memory[self.location+2])
				self.memory[a] = b
				
				self.location += 3
				
			elif nextCmd == 17: # call
				'''write the address of the next instruction to the self.stack and jump to <a>'''
				self.stack.append(self.location+2)
				self.location = self.getValue(self.memory[self.location+1])
				
			elif nextCmd == 18: # ret
				'''remove the top element from the self.stack and jump to it; empty self.stack = halt'''
				if not self.stack:
					sys.exit()
				else:
					self.location = self.stack[-1]
					self.stack = self.stack[:-1]
					
			elif nextCmd == 19: # out # ascii code of <a>
				'''write the character represented by ascii code <a> to the terminal'''
				sys.stdout.write(chr(self.getValue(self.memory[self.location+1])))
				self.location += 2
				
			elif nextCmd == 20: # in
				'''read a character from the terminal and write its ascii code to <a>;
				it can be assumed that once input starts, it will continue until a newline is encountered;
				this means that you can safely read whole lines from the keyboard and trust that they will be fully read'''
				# Check if we're currently reading something
				if self.inputHandler == None:
					# read in a new input
					inString = raw_input()
					
					# handle special keywords
					if inString == "register8":
						print self.registers[7]
						continue # do not save this obvs
					elif inString == "track":
						self.tracking = True
						continue
					elif inString == "untrack":
						self.tracking = False
						continue
					
					self.inputHandler = (char for char in inString)
				
				try:
					c = self.inputHandler.next()
				except:
					self.inputHandler = None
					c = '\n'
				
				self.registers[self.memory[self.location+1]%32768] = ord(c)
				
				self.location += 2
				
			elif nextCmd == 21: # noop
				'''no operation'''
				self.location += 1
				
			else: pass # doesn't do anything anymore; was used to fill in missing operations

# Read in from challenge.bin to memory
def main():
	# This can theoretically be altered to read in other files
	filename = "challenge.bin"
	
	vm = VM()
	
	with open(filename, 'rb') as f:
		# we read in 16 bits at a time
		c = f.read(2)
		while c != '':
			vm.memory.append(struct.unpack('<H', c)[0])
			c = f.read(2)
	
	vm.mainLoop()

if __name__ == "__main__":
	main()
