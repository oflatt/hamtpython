from array import array
from random import randint
from timeit import timeit

class Hamt:
    def __init__(self, nodesize, numbits):
        # In each node, keys are stored in the first half and values are stored in the second
        self.nodesize = nodesize
        self.numbits = numbits
        self.head = [None] * self.nodesize * 2
        pass
    
    def insert(self, key, value):
        done = False
        l = self.head
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
                    # now add both of them with the new node in place 
                    self.insert(oldkey, oldval)
                    self.insert(key, value)
                    done = True
            # go down one node
            else:
                depth += 1
                l = l[index + self.nodesize]
                # now test the next depth, loop

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
testh = 0

def populatenumbers(number):
    global randnumbers
    randnumbers = []
    for x in range(number):
        randnumbers.append(randint(0, 1000))

def testhamtinsert():
    for n in randnumbers:
        testh.insert(n, n+1)

def testhamtget():
    for n in randnumbers:
        testh.get(n)

def testtimes(number):
    global testh
    testh = Hamt(4, 2)
    populatenumbers(number)
    inserttime = timeit(testhamtinsert, number = 1)
    gettime = timeit(testhamtget, number = 1)
    print("Number of data points: " + str(number))
    print("Insert time: " + str(inserttime))
    print("Search time: " + str(gettime))

testtimes(200)
testtimes(200)
testtimes(200)
testtimes(300)
testtimes(300)
testtimes(300)
testtimes(400)
testtimes(400)
testtimes(400)
testtimes(9000)
