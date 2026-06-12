# this function will find the minimum non-occupied space (find the first L position)
def mex(values):
    mex = 0
    while mex in values:
        mex += 1
    return mex