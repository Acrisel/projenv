'''
Created on Apr 26, 2015

@author: uri
'''
from environ  import Environ
import os.path
import logging

if __name__ == '__main__':
    import unittest
    import pickle
    pickle_modules = [pickle]
    try:
        import cPickle
        pickle_modules.append(cPickle)
    except:
        pass
    
    class TestEnviron(unittest.TestCase):
        def test_simple(self):
            root_loc=os.path.dirname(__file__)
            module_loc=os.path.join(root_loc,'lvl1', 'lvl2', 'lvl3')
            module_env=Environ(osenv=True)
            module_env.loads(path=module_loc)
            print('POST ENVIRON:', repr(module_env))
            A_value = os.environ.get('A1','None')
            A_expected = '17'
            #self.assertEqual(argFoo, argBar, "These are not the same")
            self.assertEqual(A_value, A_expected, "These are not the same")
# -- this assert will fail
 
            #self.assertNotEqual(argFoo, argBar, "These are the same")
# -- this assert will succeed
 
            #argFoo = 123
            #argBar = "123"
            #self.assertEqual(argFoo, argBar, "These are not the same")
            # -- this assert will fail
            
unittest.main()
