from random import choice  # Used for ? instruction
from time import sleep  # Used for Visual mode
import getopt  # Used in another version of this code
import sys  # Same
import os
import datetime
import string
digs = string.digits + string.ascii_lowercase


def int2base(x, base):
    if x < 0: sign = -1
    elif x==0: return '0'
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[int(x % base)])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

f = ''
x = None
y = None
storeoffset = [0, 0]  # Not used for now, good to have if I'm ever adding Concurrent Funge
stackstack = [[]]     # Stack stack needed instead of singular stack for Funge-98 compatibility
stringmode = False    # String mode is used to make the IP not execute commands while in a string.
skipcounter = 0       # This is used for the 'j' instruction
repeatcounter = 0     # Used for the 'k' instruction
tempdelta = [0, 1]    # Used for wrapping
delta = [0, 1]        # Direction the IP is traveling in
outputstring = ''     # Used for Debug mode.
inComment = False     # For ';', the comment instruction.
origin = [0, 0]
class BASE:           # BASE fingerprint, converts between number bases.
    def B(self):      # Output binary string of a number.
        output(str(bin(pop()))[2:])

    def H(self):      # Output hexadecimal string of a number.
        output(str(hex(pop()))[2:])

    def I(self):      # Read input as a number in the base of a popped number.
        b = pop()
        good = False
        while not good:
            try:
                push(int(input(), b))
                good = True
            except ValueError:
                good = False

    def N(self):      # Convert a popped number to a popped base.
        output(int2base(pop(), pop()))

    def O(self):      # Output octal string of a number.
        output(oct(pop())[2:])


class MODU:          # MODU fingerprint does modulus.
    def M(self):     # Modulus of two popped numbers (in order unlike '%')
        push(pop() % pop())

    def U(self):     # Unsigned modulus of two popped numbers.
        push(abs(pop() % pop()))

    def R(self):     # This is supposed to be the 'C-language modulus'. I dunno what to do with it.
        push(pop() % pop())


class ROMA:          # ROMA fingerprint does Latin numbers. Should be obvious what they do.
    def I(self):
        push(1)

    def V(self):
        push(5)

    def X(self):
        push(10)

    def L(self):
        push(50)

    def C(self):
        push(100)

    def D(self):
        push(500)

    def M(self):
        push(1000)
BASE = BASE()
MODU = MODU()
ROMA = ROMA()
fingerDict = {0x42415345: {'B': BASE.B,               # Dictionary of fingerprint functions.
                           'H': BASE.H,
                           'I': BASE.I,
                           'N': BASE.N,
                           'O': BASE.O},
              0x4E554C4C: dict((letter, None) for letter in string.ascii_uppercase),  # This one is NULL. It resets the fingerprints.
              0x4D4F4455: {'M': MODU.M,
                           'U': MODU.U,
                           'R': MODU.R},
              0x524F4D41: {'I': ROMA.I,
                           'V': ROMA.V,
                           'X': ROMA.X,
                           'L': ROMA.L,
                           'C': ROMA.C,
                           'D': ROMA.D,
                           'M': ROMA.M}}
currentFuncts = dict((letter, None) for letter in string.ascii_uppercase)  # Current fingerprint functions bound to A-Z

prevSem = dict(currentFuncts)  # Previous fingerprints for restoring.



def load(fingerprint):  # Load a fingerprint.
    if fingerprint in fingerDict:
        for (letter, func) in fingerDict[fingerprint].items():
            prevSem[letter] = currentFuncts[letter]
            currentFuncts[letter] = func
        push(fingerprint); push(1)
    else:
        global delta
        delta = [-x for x in delta]


def unload(fingerprint):  # Unload a fingerprint.
    if fingerprint in fingerDict:
        for letter, func in fingerDict[fingerprint].items():
            currentFuncts[letter] = prevSem[letter]
            prevSem[letter] = None
    else:
        global delta
        delta = [-x for x in delta]


def output(x):  # Output something :P
    global outputstring
    print(x, end="")
    outputstring += str(x)


def sysinfo(num):  # For instruction 'y' which asks for a shit load of system information for some reason.
    tempstackstack = stackstack
    global f
    push(0); count = 1
    for e, v in dict(os.environ).items():  # Environment variables.
        push(0); count += 1
        for c in v[::-1]:
            push(ord(c)); count += 1
        push(ord('=')); count += 1
        for c in e[::-1]:
            push(ord(c)); count += 1
    push(0); push(0)
    for i in sys.argv:  # Command line arguments
        push(0); count += 1
        for c in i[::-1]:
            push(ord(c)); count += 1
    push(0); count += 1
    for c in f[::-1]:  # Plus filename.
        push(ord(c)); count += 1
    for i in tempstackstack:  # Length of stacks in the stack stack.
        push(len(i)); count += 1
    push(len(stackstack)); count += 1  # Length of stack stack.
    time = datetime.time()
    date = datetime.date.today()
    push(time.hour * 256 * 256 + time.minute * 256 + time.second); count += 1  # Date shenanigans.
    push((date.year - 1900) * 256 * 256 + date.month * 256 + date.day); count += 1  # Time shenanigans.
    push(len(m[0])-origin[1]); push(len(m)-origin[0]); count += 2  # Highest point containing a non-space character.
    push(-origin[1]); push(-origin[0]); count += 2  # Lowest point containing a non-space character.
    push(storeoffset[1]); push(storeoffset[0]); count += 2  # Storage offset.
    push(delta[1]); push(delta[0]); count += 2  # Delta.
    push(x-origin[1]); push(y-origin[0]); count += 2  # Coordinates.
    push(0); push(0); count += 2  # ID and Team number of IP. This is important in Concurrent Funge.
    push(len(delta)); count += 1  # Dimensions in Funge-Space, aka 2.
    push(ord(os.pathsep)); count += 1  # Path separator character (this is not accurate)
    push(0); count += 1  # Erm. I don't quite remember what this one is.
    push(1); count += 1  # Version of the interpreter
    push(29358); count += 1  # Arbitrary handprint of the interpreter.
    push(float('inf')); count += 1  # Amount of bytes per Funge-Space cell.
                                    # Since Python has unlimited numbers, this is infinite.
    push(0); count += 1  # Some binary flags about things being implemented. None of it's implemented.
    if num > 0:
        if num == 13:
            num = 12
        a = stackstack[-1][-num] if len(stackstack[-1]) > num else 0
        for i in range(count):
            pop()
        push(a)


def move(x, y):  # Moving and wrapping. The wrapping algorithm is called Lahey-Space.
    global m, delta
    if x + delta[1] not in range(0, len(m[y])) or y + delta[0] not in range(0, len(m)):
        delta = [-x for x in delta]
        while x + delta[1] in range(0, len(m[y])) and y + delta[0] in range(0, len(m[y])):
            x += delta[1]
            y += delta[0]
        delta = [-x for x in delta]
    else:
        x += delta[1]
        y += delta[0]
    return x, y


def exec(char):  # Execute an instruction.
    global stringmode, delta, tempdelta, repeatcounter, skipcounter, storeoffset, m, outputstring, y, x, inComment, origin
    if char == ' ':  # Skips all spaces, so that spaces don't take up a tick.
        if stringmode:  # Yes, even in string mode. This makes it impossible to have multiple consecutive spaces
            push(32)    # in a string.
        while char == ' ':
            x, y = move(x, y)
            char = chr(m[y][x])
    if not stringmode and not inComment:
        if char == '>':  # Makes the IP move right.
            delta = [0, 1]
        elif char == '<':  # Makes the IP move left.
            delta = [0, -1]
        elif char == '^':  # Makes the IP move up.
            delta = [-1, 0]
        elif char == 'v':  # Makes the IP move down.
            delta = [1, 0]
        elif char == '"':  # Initiates string mode.
            stringmode = True
        elif char == ',':  # Pops a character on top of the stack and prints it.
            try:
                a = chr(pop())
                output(a)
            except:
                pop()
                output(' ')
        elif char == '.':  # Pops a number on top of the stack and prints it.
            output(pop())
        elif char == '?':  # Sends the IP in a random cardinal direction.
            delta = choice([[0, 1], [0, -1], [1, 0], [-1, 0]])
        elif char in [str(hex(x))[2:] for x in range(0, 16)]:
            push(int('0x' + str(char), 16))
        elif char == '#':  # Skips one instruction
            skipcounter += 1
        elif char == 'j':  # Pops a number off the stack and skips that many instructions.
            skipcounter += pop()
        elif char == 'k':  # Pops a number off the stack and executes the next instruction that many times.
            tempdelta = delta
            a = pop()
            if a > 0:
                i, j = move(x, y)
                while chr(m[j][i]) == ' ' or chr(m[j][i]) == ';':
                    i, j = move(i, j)
                for k in range(a):
                    exec(chr(m[j][i]))
            else:
                skipcounter += 1
        elif char == '+':  # Pops two numbers, adds them, and pushes the result in.
            b = pop()
            a = pop()
            push((a+b))
        elif char == '-':  # Pops two numbers, subtracts the first from the second, and pushes the result in
            b = pop()
            a = pop()
            push(a-b)
        elif char == '*':  # Pops two numbers, multiplies them, and pushes the result in.
            b = pop()
            a = pop()
            push(a*b)
        elif char == '/':  # Pops two numbers, divides the first by the second using integer division,
            b = pop()              # and pushes the result in.
            a = pop()
            push(a//b if b != 0 else 0)
        elif char == '%':  # Pops two numbers, divides the first by the second using integer division,
            b = pop()              # and pushes the modulus in.
            a = pop()
            push(a % b if b != 0 else 0)
        elif char == '\\':  # Pops two elements and pushes them in in reverse order, swapping them.
            b = pop()
            a = pop()
            push(b)
            push(a)
        elif char == "'":            # Pushes the ASCII value of the next instruction.
            x, y = move(x, y)
            push(m[y][x])  # Effectively a one-instruction string mode.
        elif char == '$':  # Pops an element off the stack.
            pop()
        elif char == ':':  # Duplicates the top element of the stack.
            a = pop()
            push(a)
            push(a)
        elif char == 'n':  # Clears the stack.
            stackstack[-1].clear()
        elif char == 'g':  # Gets the ASCII value of the instruction on the location of a popped vector.
            a = pop()
            b = pop()
            if a+storeoffset[0]+origin[0] >= 0 and b+storeoffset[1]+origin[1] >= 0:
                try:
                    push(m[a+storeoffset[0]+origin[0]][b+storeoffset[1]+origin[1]])
                except:  # Pushes a space if out of bounds.
                    push(32)
            else:
                push(32)
        elif char == 'p':  # Sets the ASCII value of the instruction on the location of a popped vector.
            a = pop()              # Modifies the program itself.
            b = pop()
            c = pop()
            while a+storeoffset[0] < -origin[0]:  # This code is messy.
                m = [[32 for i in range(max([len(k) for k in m]))]] + m
                y += 1
                origin[0] += 1
            while b+storeoffset[1] < -origin[1]:
                for i in range(len(m)):
                    m[i] = [32] + m[i]
                x += 1
                origin[1] += 1
            good = False
            while not good:
                try:
                    m[a + storeoffset[0] + origin[0]][b + storeoffset[1] + origin[1]] = c
                    good = True
                    for i in range(len(m)):
                        m[i] = [(m[i][x] if x < len(m[i]) else 32) for x in range(max([len(k) for k in m]))]
                except:  # Expands the program if the popped vector is out of bounds.
                    while a+storeoffset[0]+origin[0] >= len(m):
                        m.append([32 for x in m[0]])
                    while b+storeoffset[1]+origin[1] >= len(m[a+storeoffset[0]+origin[0]]):
                        m[a+storeoffset[0]+origin[0]].append(32)

        elif char == '!':  # pops a number a off the stack, and pushes NOT a.
            a = pop()
            if a == 0:
                a = 1
            else:
                a = 0
            push(a)
        elif char == '`':  # pops two numbers off the stack, and pushes 1 if the second is greater than
            a = pop()              # the first, else it pushes 0.
            b = pop()
            push(0 if a >= b else 1)
        elif char == '_':  # pops a number a off the stack, and sends the IP right if a == 0, else
            a = pop()              # it sends the IP left.
            if a != 0:
                delta = [0, -1]
            else:
                delta = [0, 1]
        elif char == '|':  # pops a number a off the stack, and sends the IP down if a == 0, else
            a = pop()              # it sends the IP up.
            if a != 0:
                delta = [-1, 0]
            else:
                delta = [1, 0]
        elif char == '[':  # Turns the IP 90 degrees to the left.
            delta = [-delta[1], delta[0]]
        elif char == ']':  # Turns the IP 90 degrees to the right.
            delta = [delta[1], -delta[0]]
        elif char == 'x':  # sets the delta to a popped vector. If this delta isn't cardinal, the IP is
            a = pop()              # 'flying'. Flying does not affect execution of instructions though.
            b = pop()
            delta = [a, b]
        elif char == '&':  # Takes an integer as input and pushes it to the stack.
            good = False
            while not good:
                a = input()
                intstr = ""
                for i in range(len(a)):
                    if a[i] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        intstr += a[i]
                        i += 1
                        while i < len(a) and a[i] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            intstr += a[i]
                            i += 1
                        break
                try:
                    push(int(intstr))
                    good = True
                except:
                    good = False
        elif char == '~':  # Takes a character from input and pushes it to the stack. If it gets no input,
            try:                   # 10 (newline) is pushed.
                for i in input():
                    push(ord(i))
            except:
                push(10)
        elif char == 'w':  # pops two values a and b off the stack. Acts like '[' if a < b,
            a = pop()              # and acts like ']' if a < b. Doesn't do anything if a == b.
            b = pop()
            if a > b:
                delta = [-delta[1], delta[0]]
            elif a < b:
                delta = [delta[1], -delta[0]]
        elif char == 's':  # Pops a value off the stack and sets the instruction at
            a = pop()              # [x + delta_x, y + delta_y] to that value.
            try:
                m[y+delta[0]][x+delta[1]] = a
                for i in range(len(m)):
                        m[i] = [(m[i][x] if x < len(m[i]) else 0) for x in range(max([len(k) for k in m]))]
            except:
                while y+delta[0] >= len(m):
                    m.append([0 for x in m[0]])
                while x+delta[1] >= len(m[a]):
                    m[a+delta[0]].append(0)
        elif char == '{':  # Pushes a new stack onto the stack stack, and transfers a popped value 'a'
            a = pop()              # amount of elements from the bottom stack to the top stack, preserving order.
            try:
                stackstack.append([])
                if a > 0:
                    stackstack[-1] = stackstack[-2][-a:len(stackstack[-2])] if len(stackstack[-2]) > a else [0 for x in range(len(stackstack[-2])-a)] + stackstack[-2]
                    stackstack[-2] = stackstack[-2][0:-a] if len(stackstack[-2]) > a else []
                    stackstack[-2].append(storeoffset[1])
                    stackstack[-2].append(storeoffset[0])
                elif a < 0:
                    stackstack[-1] = []
                    for i in range(abs(a)):
                        stackstack[-1].append(0)
                storeoffset[1], storeoffset[0] = move(x, y)
                storeoffset[1] -= origin[1]
                storeoffset[0] -= origin[0]
            except MemoryError:  # Reverses the IP if no memory is available for an extra stack.
                delta = [-i for i in delta]
        elif char == '}':  # Pops a value a off the stack, pops a vector off the SOSS (second stack on the stack stack),
            if len(stackstack) > 1:  # sets the storage offset to it, then transfers a elements from the top stack
                a = pop()            # to the SOSS, then pops the top stack off the stack stack.
                storeoffset = [stackstack[-2].pop() if stackstack[-2] != [] else 0, stackstack[-2].pop() if stackstack[-2] != [] else 0]
                if a > 0:
                    stackstack[-2] += stackstack[-1][-a:] if len(stackstack[-1]) > a else [0 for x in range(a - len(stackstack[-1]))] + stackstack[-1]
                    stackstack.pop()
                elif a < 0:
                    for i in range(abs(a)):
                        stackstack[-2].pop()
                    stackstack.pop()
                else:
                    stackstack.pop()
            else:  # Reverses the IP if there's only one stack on the stack stack.
                delta = [-i for i in delta]
        elif char == 'u':  # pops a value a off the stack, then transfers a elements from the SOSS to the
                           # top stack, reversing order.
            if len(stackstack) > 1:
                a = pop()
                if a > 0:
                    for i in range(a):
                        push(stackstack[-2].pop() if stackstack[-2] != [] else 0)
                elif a < 0:
                    for i in range(a):
                        stackstack[-2].append(pop())
            else:
                delta = [-i for i in delta]
        elif char == '@':  # Ends the program.
            sys.exit(0)
        elif char == 'q':  # Exits with a popped return code.
            sys.exit(pop())
        elif char == 'z':  # 'z' is an explicit no-op.
            True
        elif char == ';':  # Initiates a comment.
            inComment = True
        elif char == 'y':  # Gets loads of system info.
            sysinfo(pop())
        elif char == '(':  # Loads a fingerprint.
            a = pop()
            if a > 0:
                z = 0
                for i in range(a):
                    c = pop()
                    z *= 256
                    z += c
                load(z)
            else:
                load(0)
        elif char == ')':  # Unloads a fingerprint.
            a = pop()
            if a > 0:
                z = 0
                for i in range(a):
                    c = pop()
                    z *= 256
                    z += c
                unload(z)
            else:
                unload(0)
        elif char in string.ascii_uppercase:  # Executes an instruction loaded by a fingerprint.
            if currentFuncts[char] is not None:
                currentFuncts[char]()
            else:
                delta = [-x for x in delta]
        else:                      # If an instruction isn't implemented, it reverses the IP.
            delta = [-i for i in delta]
    elif not inComment:  # Execute if string mode is active
        if char != '"':
            push(m[y][x])
        else:  # End string mode when encountering a " instruction.
            stringmode = False
    else:
        if char == ';':
            inComment = False


def pop():            # This is a seperate function because the Befunge stack pops 0 if nothing is there.
    return stackstack[-1].pop() if stackstack[-1] != [] else 0


def push(x):          # Put in a seperate function for brevity.
    stackstack[-1].append(x)


def execute(file):
    global y, x, delta, stackstack, outputstring, m, skipcounter
    m = open(file).read().split('\n')
    m = [[ord(j) for j in i] for i in m]
    for i in range(len(m)):
        m[i] = [(m[i][x] if x < len(m[i]) else 32) for x in range(max([len(k) for k in m]))]
    x = 0
    y = 0
    while True:
        if skipcounter != 0:  # Skipping multiple positions (for the 'j' instruction. 'k' and '#' use it too)
            if skipcounter > 0:
                while skipcounter > 0:
                    x, y = move(x, y)
                    skipcounter -= 1
            else:
                while skipcounter < 0:
                    delta = [-x for x in delta]
                    x, y = move(x, y)
                    delta = [-x for x in delta]
                    skipcounter += 1
        exec(chr(m[y][x]))
        if visual:
            m[y][x], temp = ord('.') if delta == [0, 0] else ord('\\') if delta[1] == -delta[0] else ord('|') if abs(delta[1]) > abs(delta[0]) else ord("-") if abs(delta[1]) < abs(delta[0]) else ord('/'), m[y][x]
                # The previous (way too long) line sets the IP's location to a character indicating its direction,
                # then sets a temporary value to restore the original character in that location.
            print("\n" * 10)
            print("Stack: ", end="")
            for i in stackstack[-1]:
                try:
                    print("%s (%s) | " % (str(i), chr(i)), end="")
                except:
                    print("%s | " % (str(i)), end="")
            print('\n')
            print("Script: \n%s" % str(''.join([''.join([(chr(i) if i <= 128 else ' ') for i in k] + ['\n']) for k in m])))
                # Uses some list comprehension to print the program.
            print("Output: " + outputstring)
            if debug:
                print("SOSS: ", end="")
                if len(stackstack) > 1:
                    for i in stackstack[-2]:
                        print("%s (%s) | " % (str(i),chr(i)),end="")
                else:
                    print("None")
                print("\nY: %i" % y)
                print("X: %i" % x)
                print("String Mode: " + str(stringmode))
                print("Character Executed: %s" % chr(temp))
                print("Loop counter (k): %i" % repeatcounter)
                print("Skip counter (j): %i" % skipcounter)
                print("Delta (y,x): " + str(delta))
                input()
            else:
                sleep(.5)
            m[y][x] = temp
        if slow:
            if visual:
                sleep(.5)

        x, y = move(x, y)


if __name__ == '__main__':
    visual = False
    debug = False
    slow = False
    good = False
    while not good:
        try:
            f = input("Enter befunge filename (include file extension)\n")
            open(f)
            good = True
        except:
            print("Enter a valid file name.\n")
    good = False
    while not good:
        try:
            d = input("Use debug mode? Y/N\n")
            if d.lower() in ['yes', 'y']:
                debug = True
                visual = True
            else:
                if d.lower() in ['no', 'n']:
                    debug = False
                else:
                    raise TypeError
            good = True
        except:
            print("Please enter 'y', 'n', 'yes', or 'no'.")
    good = False
    if not debug:
        while not good:
            try:
                visual = input("Use Visual mode? Y/N\n")
                if visual.lower() in ['yes', 'y']:
                    visual = True
                else:
                    if visual.lower() in ['no', 'n']:
                        visual = False
                    else:
                        raise TypeError
                good = True
            except:
                print("Please enter 'y', 'n', 'yes', or 'no'.")
    good = False
    if visual and (not debug):
        while not good:
            try:
                slow = input("Slow execution? Y/N\n")
                if slow.lower() in ['yes', 'y']:
                    slow = True
                else:
                    if slow.lower() in ['no', 'n']:
                        slow = False
                    else:
                        raise TypeError
                good = True
            except:
                print("Please enter 'y', 'n', 'yes', or 'no'.")
    execute(f)
