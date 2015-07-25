'''
Created on Apr 26, 2015

@author: uri
'''
from environ  import Environ
import os.path

import unittest
import pickle
import logging
pickle_modules = [pickle]
try:
    import cPickle
    pickle_modules.append(cPickle)
except:
    pass

logging.basicConfig(handlers=[logging.NullHandler()])
logger=logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TestEnviron(unittest.TestCase):
    def test_A_value(self):
        #logger=logging.getLogger(__name__)
        #handler = logging.StreamHandler()
        #formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        #handler.setFormatter(formatter)
        #logger.addHandler(handler)
        #logger.setLevel(logging.DEBUG)
        root_loc=os.path.dirname(__file__)
        module_loc=os.path.join(root_loc,'lvl1', 'lvl2', 'lvl3')
        module_env=Environ(osenv=True,trace_env=['U1'], ulogger=logger)
        module_env.loads(path=module_loc)
        print('POST ENVIRON:', repr(module_env))
        A1_value = os.environ.get('A1','None')
        A1_expected = '17'
        A2_expected = '27'
        B1_expected = '17'
        B2_expected = '27'
        C1_expected = '17'
        C2_expected = '27'
        #self.assertEqual(argFoo, argBar, "These are not the same")
        self.assertEqual(A1_value, A1_expected, "A1 is not correct")
# -- this assert will fail
 
            #self.assertNotEqual(argFoo, argBar, "These are the same")
# -- this assert will succeed
 
            #argFoo = 123
            #argBar = "123"
            #self.assertEqual(argFoo, argBar, "These are not the same")
            # -- this assert will fail
            
unittest.main()
