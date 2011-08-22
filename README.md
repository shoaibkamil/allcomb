# AllCombMap and AllCombMapReduce

Specializers designed to facilitated map, map-like, and map-reduce-like computations.  
The computation is either a traditional map, or one which is intended to replace code 
that looks like
    
    for x in ():
      for y in ():
        for z in ():
          do_something(x,y,z,...)

by replacing the loop with a version that returns a list with an item for each x,y,z.

## Current Usage/API
`AllCombMap(lists, func, *args).execute(nproc=n)`
where

- `lists` is a list of lists
- `func` is a side-effect free function that returns something
- `args` is the rest of arguments to pass to `func`
- `nproc` is optional argument that tells the specializer how many processes to use

The function signature for `func` must be such that it takes in `a+b`
arguments, where `a` is the number of lists, and `b` is the number of 
other arguments passed to the specializer.  The result will be a list 
that contains one item for each member in the cartesian product of 
`lists`, and that item is the result of applying `func`.

Example:

    from allcombmap import *
    
    def add(x,y):
      return x+y
    
    result = AllCombMap([[1,2,3],[3,4,5]], add).interpret()
   
`result` will be the list `[4,5,6,5,6,7,6,7,8]` in some (possibly
sorted, possibly not) order.


`AllCompMapReduce` is not yet implemented.
