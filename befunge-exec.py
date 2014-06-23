from random import choice  # Used for ? instruction
from time import sleep  # Used for Visual mode
import getopt  # Used in another version of this code
import sys  # Same


def execute(m):
    m = m.split("\n")
    for i in range(len(m)):                                                                   # Here, I make sure that
        m[i] = [(ord(x)) for x in m[i]]                                                       # m has ASCII values
    for i in range(len(m)):                                                                   # instead of characters
        m[i] = [(m[i][x] if x < len(m[i]) else 32) for x in range(max([len(k) for k in m]))]  # and that all rows in m
    x = 0                                                                                     # have the same length.
    y = 0
    storeoffset = [0, 0]  # Not used for now, good to have if I'm ever adding Concurrent Funge
    stackstack = [[]]     # Stack stack needed instead of singular stack for Funge-98 compatibility
    stringmode = False    # String mode is used to make the IP not execute commands while in a string.
    skipcounter = 0       # This is used for the 'j' instruction
    repeatcounter = 0     # Used for the 'k' instruction
    tempdelta = [0, 1]    # Used for wrapping
    delta = [0, 1]        # Direction the IP is traveling in
    outputstring = ''     # Used for Debug mode.
    def pop():            # This is a seperate function because the Befunge stack pops 0 if nothing is there.
        return stackstack[-1].pop() if stackstack[-1] != [] else 0
    def push(x):          # Put in a seperate function for brevity.
        stackstack[-1].append(x)
    while True:
        if skipcounter != 0:  # Skipping multiple positions (for the 'j' instruction)
            if skipcounter > 0:
                while skipcounter > 0:
                    if x + delta[1] not in range(0, len(m[y])) or y + delta[0] not in range(0, len(m)):  # Wrapping
                        delta = [-x for x in delta]
                        while x + delta[1] in range(0, len(m[y])) and y + delta[0] in range(0, len(m[y])):
                            x += delta[1]
                            y += delta[0]
                        delta = [-x for x in delta]
                    else:
                        x += delta[1]
                        y += delta[0]
            else:
                while skipcounter < 0:
                    if x + delta[1] not in range(0, len(m[y])) or y + delta[0] not in range(0, len(m)):  # More wrapping
                        delta = [-x for x in delta]
                        while x + delta[1] in range(0, len(m[y])) and y + delta[0] in range(0, len(m[y])):
                            x -= delta[1]
                            y -= delta[0]
                        delta = [-x for x in delta]
                    else:
                        x -= delta[1]
                        y -= delta[0]
        if chr(m[y][x]) == ' ':  # Skips all spaces, so that spaces don't take up a tick.
            if stringmode:  # Yes, even in string mode. This makes it impossible to have multiple consecutive spaces
                push(32)    # in a string.
            while chr(m[y][x]) == ' ':
                if x + delta[1] not in range(0, len(m[y])) or y + delta[0] not in range(0, len(m)):  # Wrapping again
                    delta = [-x for x in delta]
                    while x + delta[1] in range(0, len(m[y])) and y + delta[0] in range(0, len(m[y])):
                        x += delta[1]
                        y += delta[0]
                    delta = [-x for x in delta]
                else:
                    x += delta[1]
                    y += delta[0]
        if not stringmode:
            if repeatcounter > 0:   # This fragment is for the 'k' instruction, which repeats the instruction following
                repeatcounter -= 1  # it.
                delta = [0, 0]
                if repeatcounter == 0:
                    delta = tempdelta
            if chr(m[y][x]) == '>':  # Makes the IP move right.
                delta = [0, 1]
            elif chr(m[y][x]) == '<':  # Makes the IP move left.
                delta = [0, -1]
            elif chr(m[y][x]) == '^':  # Makes the IP move up.
                delta = [-1, 0]
            elif chr(m[y][x]) == 'v':  # Makes the IP move down.
                delta = [1, 0]
            elif chr(m[y][x]) == '"':  # Initiates string mode.
                stringmode = True
            elif chr(m[y][x]) == ',':  # Pops a character on top of the stack and prints it.
                try:
                    a = chr(pop())
                    print(a, end="")
                    outputstring += a
                except:
                    pop()
                    print(' ', end="")
                    outputstring += ' '
            elif chr(m[y][x]) == '.':  # Pops a number on top of the stack and prints it.
                a = pop()
                print(a, end="")
                outputstring += str(a)
            elif chr(m[y][x]) == '?':  # Sends the IP in a random cardinal direction.
                delta = choice([[0, 1], [0, -1], [1, 0], [-1, 0]])
            elif chr(m[y][x]) in [str(hex(x))[2:] for x in range(0, 16)]:
                push(int('0x' + str(chr(m[y][x])), 16))
            elif chr(m[y][x]) == '#':  # Skips one instruction
                skipcounter = 1
            elif chr(m[y][x]) == 'j':  # Pops a number off the stack and skips that many instructions.
                skipcounter = pop()
            elif chr(m[y][x]) == 'k':  # Pops a number off the stack and executes the next instruction that many times.
                tempdelta = delta
                repeatcounter = pop()
            elif chr(m[y][x]) == '+':  # Pops two numbers, adds them, and pushes the result in.
                b = pop()
                a = pop()
                push(a+b)
            elif chr(m[y][x]) == '-':  # Pops two numbers, subtracts the first from the second, and pushes the result in
                b = pop()
                a = pop()
                push(a-b)
            elif chr(m[y][x]) == '*':  # Pops two numbers, multiplies them, and pushes the result in.
                b = pop()
                a = pop()
                push(a*b)
            elif chr(m[y][x]) == '/':  # Pops two numbers, divides the first by the second using integer division,
                b = pop()              # and pushes the result in.
                a = pop()
                push(a//b if b != 0 else 0)
            elif chr(m[y][x]) == '%':  # Pops two numbers, divides the first by the second using integer division,
                b = pop()              # and pushes the modulo in.
                a = pop()
                push(a % b if b != 0 else 0)
            elif chr(m[y][x]) == '\\':  # Pops two elements and pushes them in in reverse order, swapping them.
                b = pop()
                a = pop()
                push(b)
                push(a)
            elif chr(m[y][x]) == "'":            # Pushes the ASCII value of the next instruction.
                push(m[y+delta[0]][x+delta[1]])  # Effectively a one-instruction string mode.
                skipcounter = 1
            elif chr(m[y][x]) == '$':  # Pops an element off the stack.
                pop()
            elif chr(m[y][x]) == ':':  # Duplicates the top element of the stack.
                a = pop()
                push(a)
                push(a)
            elif chr(m[y][x]) == 'n':  # Clears the stack.
                stackstack[-1].clear()
            elif chr(m[y][x]) == 'g':  # Gets the ASCII value of the instruction on the location of a popped vector.
                a = pop()
                b = pop()
                push(m[a][b])
            elif chr(m[y][x]) == 'p':  # Sets the ASCII value of the instruction on the location of a popped vector.
                a = pop()              # Modifies the program itself.
                b = pop()
                c = pop()
                good = False
                while not good:
                    try:
                        m[a + storeoffset[0]][b + storeoffset[1]] = c
                        good = True
                        for i in range(len(m)):
                            m[i] = [(m[i][x] if x < len(m[i]) else 0) for x in range(max([len(k) for k in m]))]
                    except:  # Expands the program if the popped vector is out of bounds.
                        while a >= len(m):
                            m.append([0 for x in m[0]])
                        while b >= len(m[a]):
                            m[a].append(0)
            elif chr(m[y][x]) == '!':  # pops a number a off the stack, and pushes NOT a.
                a = pop()
                if a == 0:
                    a = 1
                else:
                    a = 0
                push(a)
            elif chr(m[y][x]) == '`':  # pops two numbers off the stack, and pushes 1 if the second is greater than
                a = pop()              # the first, else it pushes 0.
                b = pop()
                push(0 if a >= b else 1)
            elif chr(m[y][x]) == '_':  # pops a number a off the stack, and sends the IP right if a == 0, else
                a = pop()              # it sends the IP left.
                if a != 0:
                    delta = [0, -1]
                else:
                    delta = [0, 1]
            elif chr(m[y][x]) == '|':  # pops a number a off the stack, and sends the IP down if a == 0, else
                a = pop()              # it sends the IP up.
                if a != 0:
                    delta = [-1, 0]
                else:
                    delta = [1, 0]
            elif chr(m[y][x]) == '[':  # Turns the IP 90 degrees to the left.
                delta = [-delta[1], delta[0]]
            elif chr(m[y][x]) == ']':  # Turns the IP 90 degrees to the right.
                delta = [delta[1], -delta[0]]
            elif chr(m[y][x]) == 'x':  # sets the delta to a popped vector. If this delta isn't cardinal, the IP is
                a = pop()              # 'flying'. Flying does not affect execution of instructions though.
                b = pop()
                delta = [b, a]
            elif chr(m[y][x]) == '&':  # Takes an integer as input and pushes it to the stack.
                good = False
                while not good:
                    a = input("Input a number:\n")
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
            elif chr(m[y][x]) == '~':  # Takes a character from input and pushes it to the stack. If it gets no input,
                try:                   # 10 (newline) is pushed.
                    for i in input():
                        push(ord(i))
                except:
                    push(10)
            elif chr(m[y][x]) == 'w':  # pops two values a and b off the stack. Acts like '[' if a < b,
                a = pop()              # and acts like ']' if a < b. Doesn't do anything if a == b.
                b = pop()
                if a > b:
                    delta = [-delta[1], delta[0]]
                elif a < b:
                    delta = [delta[1], -delta[0]]
            elif chr(m[y][x]) == 's':  # Pops a value off the stack and sets the instruction at
                a = pop()              # [x + delta_x, y + delta_y] to that value.
                try:
                    m[y+delta[0]][x+delta[1]] = a
                    for i in range(len(m)):
                            m[i] = [(m[i][x] if x < len(m[i]) else 0) for x in range(max([len(k) for k in m]))]
                except:
                    while a >= len(m):
                        m.append([0 for x in m[0]])
                    while b >= len(m[a]):
                        m[a].append(0)
            elif chr(m[y][x]) == '{':  # Pushes a new stack onto the stack stack, and transfers a popped value 'a'
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
                except MemoryError:  # Reverses the IP if no memory is available for an extra stack.
                    delta = [-i for i in delta]
            elif chr(m[y][x]) == '}':    # Pops a value a off the stack, pops a vector off the SOSS (second stack on the stack stack),
                if len(stackstack) > 1:  # sets the storage offset to it, then transfers a elements from the top stack
                    a = pop()            # to the SOSS, then pops the top stack off the stack stack.
                    storeoffset = [stackstack[-2].pop(), stackstack[-2].pop()]
                    if a > 0:
                        stackstack[-2] = stackstack[-1][-a:] if len(stackstack[-2]) > a else [0 for x in range(len(stackstack[-2])-1)] + stackstack[-2]
                        stackstack.pop()
                    elif a < 0:
                        for i in range(abs(a)):
                            stackstack[-2].pop()
                        stackstack.pop()
                    else:
                        stackstack.pop()
                else:  # Reverses the IP if there's only one stack on the stack stack.
                    delta = [-i for i in delta]
            elif chr(m[y][x]) == 'u':  # pops a value a off the stack, then transfers a elements from the SOSS to the
                a = pop()              # top stack, reversing order.
                if len(stackstack) > 1:
                    if a > 0:
                        for i in range(a):
                            push(stackstack[-2].pop() if stackstack[-2] != [] else 0)
                    elif a < 0:
                        for i in range(a):
                            stackstack[-2].append(pop())
                else:
                    delta = [-i for i in delta]
            elif chr(m[y][x]) == '@':  # Ends the program.
                break
            elif chr(m[y][x]) == 'z':  # 'z' is an explicit no-op.
                True
            else:                      # If an instruction isn't implemented, it reverses the IP.
                delta = [-i for i in delta]
        else:  # Execute if string mode is active
            if chr(m[y][x]) != '"':
                push(m[y][x])
            else:  # End string mode when encountering a " instruction.
                stringmode = False
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

        if x + delta[1] not in range(0, len(m[y])) or y + delta[0] not in range(0, len(m)):  # Wrapping (Lahey-Space)
            delta = [-x for x in delta]
            while x + delta[1] in range(0, len(m[y])) and y + delta[0] in range(0, len(m)):
                x += delta[1]
                y += delta[0]
            delta = [-x for x in delta]
        else:
            x += delta[1]
            y += delta[0]

if __name__ == '__main__':
    visual = False
    debug = False
    slow = False
    good = False
    while not good:
        try:
            f = input("Enter befunge filename (include file extension)\n")
            f = open(f).read()
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
