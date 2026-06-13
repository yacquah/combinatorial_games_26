# this function will find the minimum non-occupied space (find the first L position)
def find_next_L(Tx, size):
    for y in range(size):
        for z in range(size):
            if(Tx[z][y] == 0):
                return (z,y)
    