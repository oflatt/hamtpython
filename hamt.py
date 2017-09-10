from array import array
from random import randint
from timeit import timeit
import gc

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
                    l = l[index + self.nodesize]
                    oldindex = (oldkey >> depth*self.numbits) & (self.nodesize-1)
                    l[oldindex] = oldkey
                    l[oldindex + self.nodesize] = oldval
                    # now loop and try to put it in the new node
                    depth += 1

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

randnumbers = []

def populatenumbers(number):
    global randnumbers
    randnumbers = []
    for x in range(number):
        randnumbers.append(randint(0, 100000))
        
def testhamtinsert(nodesize, numbits, justone = False):
    newhamt = Hamt(nodesize, numbits)
    
    def makehamt():
        h = newhamt
        for n in randnumbers:
            h = h.insert(n, n+1)
        return h

    if not justone:
        for x in range(99):
            makehamt()
        
    return makehamt()

def testhamtget(testh):
    for x in range(100):
        for n in randnumbers:
            testh.get(n)

def testtimes(number, nodesize, numbits):
    populatenumbers(number)
    testhamt = testhamtinsert(nodesize, numbits, True)
    
    def testhamtinsertwrapper():
        testhamtinsert(nodesize, numbits)

    def testhamtgetwrapper():
        testhamtget(testhamt)
    
    inserttime = timeit(testhamtinsertwrapper, number = 1)
    gettime = timeit(testhamtgetwrapper, number = 1)
    
    print("Data points: " + str(number) + " node size: " + str(nodesize))
    print("Insert time: " + str(inserttime))
    print("Search time: " + str(gettime))


testtimes(512, 4, 2)
gc.collect()
testtimes(512, 8, 3)
gc.collect()
testtimes(512, 16, 4)
