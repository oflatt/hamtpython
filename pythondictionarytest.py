from random import randint
from timeit import timeit
import sys, gc
randnumbers = []

def populatenumbers(number):
    global randnumbers
    randnumbers = []
    for x in range(number):
        randnumbers.append(randint(0, 100000))
        
def testinsert(repetitions, isPersistant, justone = False):
    newdict = {}

    def makeone():
        h = newdict
        
        if isPersistant:
            for n in randnumbers:
                h = h.copy()
                h[n] = n+1
        else:
            for n in randnumbers:
                h[n] = n+1
        return h

    if not justone:
        for x in range(repetitions-1):
            makeone()
        
    return makeone()

def testget(test, repetitions):
    for x in range(repetitions):
        for n in randnumbers:
            test[n]

def getmemoryuse(l):
    memoryuse = sys.getsizeof(l)
    return memoryuse
    

def testtimes(number, repetitions, isPersistant = False):
    populatenumbers(number)
    testdict = testinsert(repetitions, isPersistant, True)
    
    def testinsertwrapper():
        testinsert(repetitions, isPersistant)

    def testgetwrapper():
        testget(testdict, repetitions)
    
    inserttime = timeit(testinsertwrapper, number = 1)
    gettime = timeit(testgetwrapper, number = 1)
    
    print("Number of data points: " + str(number) + " repetitions: " + str(repetitions))
    print("Insert time: " + str(inserttime))
    print("Search time: " + str(gettime))
    print("Memory use of one dictionary: " + str(getmemoryuse(testdict)))

print("Non-persistant use of dictionaries:")
testtimes(4, 1000)
gc.collect()
testtimes(64, 1000)
gc.collect()
testtimes(512, 50)
gc.collect()
testtimes(2048, 10)
gc.collect()
print("Persistant use of dictionaries:")
testtimes(4, 1000, True)
gc.collect()
testtimes(64, 1000, True)
gc.collect()
testtimes(512, 50, True)
gc.collect()
testtimes(2048, 10, True)
