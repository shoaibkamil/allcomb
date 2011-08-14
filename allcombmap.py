## AllCombMap
##
## Runs a function for each combination of the provided lists.

import asp
import asp.codegen.python_ast as py_ast
import asp.codegen.ast_tools as ast_tools

# Semantic Model
class IterSpaceNode(object):
    """SM node that tracks the iteration space and function."""
    def __init__(self, lists, func, *args, **kwargs):
        self.lists = lists
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._fields = ['lists', 'func']


class AllCombMapSM(object):
    """Semantic Model for all combinations map."""
    
    def __init__(self, lists, func, *args, **kwargs):
        # since we are not currently inspecting the tree,
        # we just save the function object
        
        self.tree = IterSpaceNode(lists, func, *args, **kwargs)

    def run(self):
        # should check to see if the SM is correct
        return self

    def interpret(self, nproc=1):
        """Use interpreter to do calculations."""

        def proxy_func(func, space, pipe):
            """Func is applied for each item in space, and returned via pipe."""
            output = []
            for x in space:
                output.append(func(*x))
            pipe.send(output)

        output = []
        import itertools

        iter_space = [x for x in itertools.product(*(self.tree.lists))]
        each_space_len = len(iter_space)/nproc
        leftover_len = len(iter_space)-(each_space_len*nproc)

        print "Length of iteration space: %d" % len(iter_space)
        print "Each of %d procs will do %d" % (nproc, each_space_len)
        print "Master will do %d extra" % leftover_len

        from multiprocessing import Process, Pipe
        pipes = []
        processes = []

        # for each child process, spawn a process and a pipe to recv the answer
        for x in xrange(nproc-1):
            child_conn, parent_conn = Pipe()
            pipes.append(parent_conn)
            space = iter_space[x*each_space_len:(x+1)*each_space_len]
            print "Spawning process to do %s" % str(space)
            processes.append(Process(target=proxy_func, args=(self.tree.func, space, child_conn)))
            processes[x].start()

        # do local work
        for x in iter_space[(nproc-1)*each_space_len:]:
            output.append(self.tree.func(*x))

        # get back work done from children & terminate them
        for x in xrange(nproc-1):
            output.extend(pipes[x].recv())
            processes[x].join()
        

        return output
            



