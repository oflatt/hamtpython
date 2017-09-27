from array import array
from random import randint
from timeit import timeit
import gc, sys

print("Hamt testing with various node sizes. Times measured in seconds, and memory use in bytes.")


class Hamt:
    def __init__(self, nodesize, numbits, head = None):
        # In each node, keys are stored in the first half and values are stored in the second
        self.nodesize = nodesize
        self.bitmapoffset = 1
        self.numbits = numbits
        if head == None:
            self.head = [0]
        else:
            self.head = head
        pass
    
    def insert(self, key, value):
        done = False
        # make a new list, but not copy items in the list
        newhead = self.head.copy()
        l = newhead
        depth = 0
        while not done:
            # get the two bits for this depth
            index = (key >> depth*self.numbits) & (self.nodesize-1)
            bitmap = l[0]
            nodelength = bin(bitmap).count("1")
            lengthafter = bin(bitmap >> index).count("1")
            #this has the bitmap accounted for
            lengthoflist = len(l)
            listindex = lengthoflist-nodelength-lengthafter
            secondlistindex = lengthoflist - lengthafter
            
            # We place the key and value in the node if it's not occupied
            if not (bitmap >> index) & 1:
                #set the bit in the bitmap to 1
                mask = 1 << index
                l[0] = bitmap | mask
                # now insert in right place, growing list
                l.insert(listindex, key)
                #can't use secondlistindex because not the list has changed size
                l.insert(len(l)-lengthafter, value)
                done = True
            # there is a collision
            elif isinstance(l[listindex], int):
                oldkey = l[listindex]
                oldval = l[secondlistindex]
                if oldval == value:
                    done = True
                else:
                    # key value now notes that it is a subnode
                    l[listindex] = 's'
                    #new list with empty bitmap
                    l[secondlistindex] = [0]
                    # now add the old one with the new node in place
                    depth += 1
                    l = l[secondlistindex]
                    #set the bit in the bitmap to 1
                    oldindex = (oldkey >> depth*self.numbits) & (self.nodesize-1)
                    mask = 1 << oldindex
                    l[0] = mask
                    l.append(oldkey)
                    l.append(oldval)
                    # now loop and try to put it in the new node

            # go down one node
            else:
                depth += 1
                l = l[secondlistindex]
                # now test the next depth, loop

        return Hamt(self.nodesize, self.numbits, newhead)

    def get(self, key):
        done = False
        value = None
        l = self.head
        depth = 0
        while not done:
            # get the two bits for this depth
            index = (key >> depth*self.numbits) & (self.nodesize-1)
            bitmap = l[0]
            nodelength = bin(bitmap).count("1")
            lengthafter = bin(bitmap >> index).count("1")
            #this has the bitmap accounted for
            lengthoflist = len(l)
            listindex = lengthoflist-nodelength-lengthafter
            secondlistindex = lengthoflist - lengthafter
            if l[listindex] == 's':
                depth += 1
                l = l[secondlistindex]
            else:
                value = l[secondlistindex]
                done = True
        return value

# test cases
newhamt = Hamt(4, 2)
def gethead(list):
    h = newhamt
    for x in list:
        h = h.insert(x, x+1)
    return h.head

def testlist(l, expected):
    t = gethead(l)
    if t != expected:
        print(t)
        print("expected: " + str(expected))

testlist([0, 1, 2], [7,0, 1, 2, 1, 2, 3])
testlist([1, 2,0], [7,0, 1, 2, 1, 2, 3])
testlist([0,2, 3], [13, 0,2, 3,1, 3, 4])
testlist([0,1,2,3], [15,0,1,2,3,1,2,3,4])
testlist([0,2, 3, 1], [15,0,1,2,3,1,2,3,4])
testlist([3,2,1,0], [15,0,1,2,3,1,2,3,4])
testlist([3,1,2,0], [15,0,1,2,3,1,2,3,4])
biglist = [424, 64, 34523, 23454, 23434, 1231, 3423 ,53453 ,345345]
testlist(biglist, gethead(reversed(biglist)))

randnumbers = []

def populatenumbers(number):
    global randnumbers
    randnumbers = []
    for x in range(number):
        randnumbers.append(randint(0, 100000))
        
def testhamtinsert(numkeys, nodesize, numbits, repetitions, justone = False):
    nhamt = Hamt(nodesize, numbits)
    randnumberslength = len(randnumbers)
    
    def makehamt(offset):
        h = nhamt
        for n in range(numkeys):
            lindex = (n+offset)%randnumberslength
            h = h.insert(randnumbers[lindex], randnumbers[lindex]+1)
        return h

    if not justone:
        for x in range(repetitions-1):
            makehamt(x*numkeys)
        
    return makehamt(0)

def testhamtget(number, testh, repetitions):
    for x in range(repetitions):
        for n in range(number):
            testh.get(randnumbers[n])

def getmemoryuse(l):
    memoryuse = sys.getsizeof(l)
    for x in l:
        if isinstance(x, list):
            memoryuse += getmemoryuse(x)
    return memoryuse

def testtimes(number, nodesize, numbits, repetitions):
    populatenumbers(number+1000)
    #testhamt = testhamtinsert(number, nodesize, numbits, repetitions, True)
    
    def testhamtinsertwrapper():
        testhamtinsert(number, nodesize, numbits, repetitions)

    #def testhamtgetwrapper():
    #    testhamtget(number, testhamt, repetitions)
    
    inserttime = timeit(testhamtinsertwrapper, number = 1)
    #gettime = timeit(testhamtgetwrapper, number = 1)

    print(str(inserttime) + ",", end='')
    #print("Number of data points: " + str(number) + " node size: " + str(nodesize) + " repetitions: " + str(repetitions))
    #print("Insert time: " + str(inserttime))
    #print("Search time: " + str(gettime))
    #print("Memory use of one hamt: " + str(getmemoryuse(testhamt.head)))

print("Iterations,Number of Keys,4,8,16,32,64,128")
print("10000,4,", end='')
testtimes(4, 4, 2, 10000)
testtimes(4, 8, 3, 10000)
testtimes(4, 16, 4, 10000)
testtimes(4, 32, 5, 10000)
testtimes(4, 64, 6, 10000)
testtimes(4, 128, 7, 10000)
print("")
print("500,64,", end='')
testtimes(64, 4, 2, 500)
testtimes(64, 8, 3, 500)
testtimes(64, 16, 4, 500)
testtimes(64, 32, 5, 500)
testtimes(64, 64, 6, 500)
testtimes(64, 128, 7, 500)
print("")
print("50,512,", end='')
testtimes(512, 4, 2, 50)
testtimes(512, 8, 3, 50)
testtimes(512, 16, 4, 50)
testtimes(512, 32, 5, 50)
testtimes(512, 64, 6, 50)
testtimes(512, 128, 7, 50)
print("")
print("10,2048,", end='')
testtimes(2048, 4, 2, 10)
testtimes(2048, 8, 3, 10)
testtimes(2048, 16, 4, 10)
testtimes(2048, 32, 5, 10)
testtimes(2048, 64, 6, 10)
testtimes(2048, 128, 7, 10)
