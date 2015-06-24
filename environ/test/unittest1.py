'''
Created on Apr 26, 2015

@author: uri
'''
from environ import Environ

if __name__ == '__main__':
    import unittest
    import pickle
    pickle_modules = [pickle]
    try:
        import cPickle
        pickle_modules.append(cPickle)
    except:
        pass

    env=Environ()
    print (env)
    
    class TestEnviron(unittest.TestCase):
        def test_simple(self):
            argFoo = "narf"
            argBar = "zort"
            #self.assertEqual(argFoo, argBar, "These are not the same")
            self.assertEqual(argFoo, argFoo, "These are not the same")
# -- this assert will fail
 
            self.assertNotEqual(argFoo, argBar, "These are the same")
# -- this assert will succeed
 
            argFoo = 123
            argBar = "123"
            self.assertEqual(argFoo, argBar, "These are not the same")
            # -- this assert will fail
            
unittest.main()
