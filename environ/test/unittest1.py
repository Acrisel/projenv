'''
Created on Apr 26, 2015

@author: uri
'''
from packageenv  import Environ
import os.path


if __name__ == '__main__':
    import unittest
    import pickle
    import logging
    pickle_modules = [pickle]
    try:
        import cPickle
        pickle_modules.append(cPickle)
    except:
        pass
    logger=logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    root_loc=os.path.dirname(__file__)
    module_loc=os.path.join(root_loc,'lvl1', 'lvl2', 'lvl3')
    module_env=Environ(osenv=True,trace_env=['T1','T2','T3','T4','T5','T6'], ulogger=logger)
    module_env.loads(path=module_loc)
    
    class TestEnviron(unittest.TestCase):
        def test_Dot_Projectenv_value(self):
            #T1 - Test for setting env variable in .projectenv locally
            #print('POST ENVIRON:', repr(module_env))
            T1_value = os.environ.get('T1','None')
            T1_expected = 'D_PR_LOC'
            self.assertEqual(T1_value, T1_expected, "T1 is not correct")
            
        def test_Dot_Projectenv_value_override(self):
            #T2 - Test for setting env variable in .projectenv locally with override False
            #print('POST ENVIRON:', repr(module_env))
            T2_value = os.environ.get('T2','None')
            T2_expected = 'D_PACK_LOC'
            self.assertEqual(T2_value, T2_expected, "T2 is not correct - should be taken from .projectenv and not overwritten")
            
        def test_Package_value(self):
            #T2 - Test for setting env variable in .projectenv locally with override False
            #print('POST ENVIRON:', repr(module_env))
            T3_value = os.environ.get('T3','None')
            T3_expected = 'PACK_LOC_T3'
            self.assertEqual(T3_value, T3_expected, "T3 is not correct - should be taken from packageenv")
            
        def test_L1_2_3_Package_value(self):
            #T2 - Test for setting env variable in .projectenv locally with override False
            #print('POST ENVIRON:', repr(module_env))
            T4_value = os.environ.get('T4','None')
            T4_expected = 'T4_L1'
            self.assertEqual(T4_value, T4_expected, "T4 is not correct - should be taken from packageenv in L1")
            T5_value = os.environ.get('T5','None')
            T5_expected = 'T5_L2'
            self.assertEqual(T5_value, T5_expected, "T5 is not correct - should be taken from packageenv in L2")
            T6_value = os.environ.get('T6','None')
            T6_expected = 'T6_L3'
            self.assertEqual(T6_value, T6_expected, "T6 is not correct - should be taken from packageenv in L3")        
unittest.main()
