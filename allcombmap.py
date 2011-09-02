## AllCombMap
##
## Runs a function for each combination of the provided lists.

import asp
import asp.codegen.python_ast as py_ast
import asp.codegen.ast_tools as ast_tools
from asp.util import *

class AllCombMap(object):
    """
    User-visible class for AllCombMap specializer.
    Usage: AllCombMap(lists, func, ...).execute()
    """
    def __init__(self, lists, func, *args):
        if lists != [] and not isinstance(lists[0], list):
            raise asp.SpecializationError("lists argument must be a list of lists or empty.")
        
        self.sm = AllCombMapSM(lists, func, *args)
        self.nproc = None

    def execute(self, nproc=None):
        """Execute the map.  If nproc is not passed in, detect it."""
        if self.nproc == None and nproc == None:
            try:
                import asp.config
                nproc = asp.config.PlatformDetector().get_cpu_info()['numCores']
            except:
                nproc = 2
        self.nproc = self.nproc or nproc
        return self.sm.interpret(nproc=nproc)

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

        def proxy_func(func, space, pipe, args):
            """Func is applied for each item in space, and returned via pipe."""
            output = []
            for x in space:
                x = x + args
                output.append(func(*x))
            pipe.send(output)

        output = []
        import itertools

        iter_space = [x for x in itertools.product(*(self.tree.lists))]
        each_space_len = len(iter_space)/nproc
        leftover_len = len(iter_space)-(each_space_len*nproc)

        debug_print("Length of iteration space: %d" % len(iter_space))
        debug_print("Each of %d procs will do %d" % (nproc, each_space_len))
        debug_print("Master will do %d extra" % leftover_len)
        debug_print("Additional args: %s" % str(self.tree.args))

        from multiprocessing import Process, Pipe
        pipes = []
        processes = []

        # for each child process, spawn a process and a pipe to recv the answer
        for x in xrange(nproc-1):
            child_conn, parent_conn = Pipe()
            pipes.append(parent_conn)
            space = iter_space[x*each_space_len:(x+1)*each_space_len]
            debug_print("Spawning process to do %s" % str(space))
            processes.append(Process(target=proxy_func, args=(self.tree.func, space, child_conn, self.tree.args)))
            processes[x].start()

        # do local work
        for x in iter_space[(nproc-1)*each_space_len:]:
            x = x + self.tree.args
            output.append(self.tree.func(*x))

        # get back work done from children & terminate them
        # use Python's select() support to do it as procs finish
        import select
        finished_procs = 0
        while finished_procs < nproc-1:
            # wait for some of the pipes to be ready to read
            ready_list, _, _ = select.select(pipes, [], [])

            for x in ready_list:
                output.extend(x.recv())
                # join() on the corresponding proc
                processes[pipes.index(x)].join()
                finished_procs += 1

        return output
            



