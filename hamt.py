from random import randint
from timeit import timeit
import gc, sys

print("Hamt testing with various node sizes. Times measured in seconds, and memory use in bytes.")

class Hamt:
    def __init__(self, nodesize, numbits, head = None):
        # In each node, keys are stored in the first half and values are stored in the second
        self.nodesize = nodesize
        self.numbits = numbits
        if head == None:
            self.head = [None] * self.nodesize * 2
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
            # We place the key and value in the node
            if l[index] == None:
                l[index] = key
                l[index + self.nodesize] = value
                done = True
            # there is a collision
            elif isinstance(l[index], int):
                oldkey = l[index]
                oldval = l[index + self.nodesize]
                if oldval == value:
                    done = True
                else:
                    # key value now notes that it is a subnode
                    l[index] = 's'
                    l[index + self.nodesize] = [None] * self.nodesize * 2
                    # now add the old one with the new node in place
                    depth += 1
                    l = l[index + self.nodesize]
                    oldindex = (oldkey >> depth*self.numbits) & (self.nodesize-1)
                    l[oldindex] = oldkey
                    l[oldindex + self.nodesize] = oldval
                    # now loop and try to put it in the new node

            # go down one node
            else:
                depth += 1
                l = l[index + self.nodesize]
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
            if l[index] == 's':
                depth += 1
                l = l[index + self.nodesize]
            else:
                value = l[index + self.nodesize]
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

testlist([0,1,2,3], [0,1,2,3,1,2,3,4])
testlist([0,2, 3, 1], [0,1,2,3,1,2,3,4])
testlist([3,2,1,0], [0,1,2,3,1,2,3,4])
testlist([3,1,2,0], [0,1,2,3,1,2,3,4])
biglist = [424, 64]
testlist(biglist, gethead(reversed(biglist)))

randnumbers = []

def populatenumbers(number):
    global randnumbers
    randnumbers = []
    for x in range(number):
        randnumbers.append(randint(0, 100000))
        
def testhamtinsert(nodesize, numbits, repetitions, justone = False):
    newhamt = Hamt(nodesize, numbits)
    
    def makehamt():
        h = newhamt
        for n in randnumbers:
            h = h.insert(n, n+1)
        return h

    if not justone:
        for x in range(repetitions-1):
            makehamt()
        
    return makehamt()

def testhamtget(testh, repetitions):
    for x in range(repetitions):
        for n in randnumbers:
            testh.get(n)

def getmemoryuse(l):
    memoryuse = sys.getsizeof(l)
    for x in l:
        if isinstance(x, list):
            memoryuse += getmemoryuse(x)
    return memoryuse
    

def testtimes(number, nodesize, numbits, repetitions):
    populatenumbers(number)
    testhamt = testhamtinsert(nodesize, numbits, repetitions, True)
    
    def testhamtinsertwrapper():
        testhamtinsert(nodesize, numbits, repetitions)

    def testhamtgetwrapper():
        testhamtget(testhamt, repetitions)
    
    inserttime = timeit(testhamtinsertwrapper, number = 1)
    gettime = timeit(testhamtgetwrapper, number = 1)
    
    print("Number of data points: " + str(number) + " node size: " + str(nodesize) + " repetitions: " + str(repetitions))
    print("Insert time: " + str(inserttime))
    print("Search time: " + str(gettime))
    print("Memory use of one hamt: " + str(getmemoryuse(testhamt.head)))

testtimes(4, 4, 2, 1000)
gc.collect()
testtimes(4, 8, 3, 1000)
gc.collect()
testtimes(4, 16, 4, 1000)
gc.collect()
testtimes(64, 4, 2, 1000)
gc.collect()
testtimes(64, 8, 3, 1000)
gc.collect()
testtimes(64, 16, 4, 1000)
gc.collect()
testtimes(512, 4, 2, 50)
gc.collect()
testtimes(512, 8, 3, 50)
gc.collect()
testtimes(512, 16, 4, 50)
gc.collect()
testtimes(2048, 4, 2, 10)
gc.collect()
testtimes(2048, 8, 3, 10)
gc.collect()
testtimes(2048, 16, 4, 10)
