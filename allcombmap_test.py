import unittest2 as unittest
from allcombmap import *

class AllCombMapTests(unittest.TestCase):
    def test_basic(self):
        def foo(x,y):
            return x+y

        ret = AllCombMap([[1,2,3,4,5]], foo, 4).execute()
        answer = map(lambda x: x+4, [1,2,3,4,5])

        ret.sort()
        answer.sort()

        self.assertEqual(ret, answer)

class SMTests(unittest.TestCase):
    def test_building_SM(self):
        def foo(x):
            return x

        sm = AllCombMapSM([[1,2,3]], foo).run()

        self.assertEqual(sm.tree.lists[0], [1,2,3])
        self.assertEqual(sm.tree.func, foo)

    def test_interpreting_SM(self):
        def foo(x):
            return -x


        sm = AllCombMapSM([[1,2,3,4]], foo).run()
        x = sm.interpret(nproc=2)

        
        space = [-1, -2, -3, -4]
        space.sort()
        x.sort()
        
        self.assertEqual(x, space)

    def test_interpreting_complicated_SM(self):
        def foo(x,y):
            return x+y
        
        sm = AllCombMapSM([[1,2,3,4],[1,2,3,4]], foo).run()
        ret = sm.interpret(nproc=3)
        
        import itertools
        answer = [x+y for x,y in itertools.product([1,2,3,4],[1,2,3,4])]
        ret.sort()
        answer.sort()

        self.assertEqual(ret, answer)

    def test_with_extra_args(self):
        def foo(x,y):
            return x+y
        sm = AllCombMapSM([[1,2,3,4]], foo, 3).run()
        ret = sm.interpret(nproc=2)

        answer = map(lambda x: x+3, [1,2,3,4])
        answer.sort()
        ret.sort()

        self.assertEqual(ret, answer)
        
        

if __name__ == '__main__':
    unittest.main()
        
