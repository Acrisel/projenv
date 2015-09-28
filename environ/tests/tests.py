'''
Created on Apr 26, 2015

@author: uri
'''
from projenv  import Environ
from projenv import EnvVar
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
    logger=logging.getLogger('Unit_test')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    root_loc=os.path.dirname(__file__)
    module_loc=os.path.join(root_loc,'lvl1', 'lvl2', 'lvl3')
    
    #TODO: Move to Test case by using assertRaises
    module_env=Environ(osenv=True,trace_env=['T1','T18'], logclass="Unit_test")
    module_env.loads(path=module_loc)
    #print('POST ENVIRON:', repr(module_env))
    
    class TestEnviron(unittest.TestCase):
        def test_Dot_Projectenv_value(self):
            #T1 - Test for setting env variable in .projectenv locally
            T1_value = module_env.get('T1')
            T1_expected = 'T1_D_PR_LOC'
            self.assertEqual(T1_value, T1_expected, "T1 is not correct")
            
        def test_Dot_Projectenv_value_override(self):
            #T2 - Test for setting env variable in .projectenv locally with override False
            #print('POST ENVIRON:', repr(module_env))
            T2_value = module_env.get('T2')
            T2_expected = 'T2_D_PR_LOC'
            self.assertEqual(T2_value, T2_expected, "T2 is not correct - should be taken from .projectenv and not overwritten")
            
        def test_Package_value(self):
            #T3 - Test for setting env variable in projenv locally after overwriting .projectenv 
            T3_value = module_env.get('T3')
            T3_expected = 'T3_PACK_LOC'
            self.assertEqual(T3_value, T3_expected, "T3 is not correct - should be taken from projenv")
            
            #T3_N_EXP - Test that export = False prevents from exporting variable
            T3_N_value = os.environ.get('T3_N_EXP','None')
            T3_N_expected = 'None'
            self.assertEqual(T3_N_value, T3_N_expected, "T3_N_EXP is not correct - should be undefined due to export = False")
            
        def test_L1_2_3_Package_value(self):
            #T4 - Test for setting env variable in projenv level lvl1
            #T5 - Test for setting env variable in projenv level lvl2
            #T6 - Test for setting env variable in projenv level lvl3
            T4_value = module_env.get('T4')
            T4_expected = 'L1_T4'
            self.assertEqual(T4_value, T4_expected, "T4 is not correct - should be taken from projenv in L1")
            T5_value = module_env.get('T5')
            T5_expected = 'L2_T5'
            self.assertEqual(T5_value, T5_expected, "T5 is not correct - should be taken from projenv in L2")
            T6_value = module_env.get('T6')
            T6_expected = 'T6_L3'
            self.assertEqual(T6_value, T6_expected, "T6 is not correct - should be taken from projenv in L3")   
            
        def test_L1_2_3_Package_value_override(self):
            #T7 - Test for lvl2 override of lvl1
            T7_value = module_env.get('T7')
            T7_expected = 'L2_T7'
            self.assertEqual(T7_value, T7_expected, "T7 is not correct - should be taken from projenv in L2")         
            #T8 - Test for lvl3 override of lvl2
            T8_value = module_env.get('T8')
            T8_expected = 'L3_T8'
            self.assertEqual(T8_value, T8_expected, "T8 is not correct - should be taken from projenv in L3")
            #T9 - Test for lvl3 override of lvl1
            T9_value = module_env.get('T9')
            T9_expected = 'L3_T9'
            self.assertEqual(T9_value, T9_expected, "T9 is not correct - should be taken from projenv in L3")
            
        def test_L1_Root_value_override(self):
            #T10 - Test for lvl1 override of .projectenv
            T10_value = module_env.get('T10')
            T10_expected = 'L1_T10'
            self.assertEqual(T10_value, T10_expected, "T10 is not correct - should be taken from projenv in L1")         
            #T8 - Test for lvl3 override of lvl2
            T8_value = module_env.get('T8')
            T8_expected = 'L3_T8'
            self.assertEqual(T8_value, T8_expected, "T8 is not correct - should be taken from projenv in L3")
            
        def test_L1_Cast_value(self):
            #T11_Int - Test for value and type
            T11_value = module_env.get('T11_Int')
            T12_value = module_env.get('T12_Float')
            T13_value = module_env.get('T13_List')
            T14_value = module_env.get('T14_Dict')
            T15_value = module_env.get('T15_None')
            T16_value = module_env.get('T16_Tuple')
            T17_value = module_env.get('T17_Bool')
            T18_value = module_env.get('T18_Expr')
            #print("T18_value =",T18_value )
            T11_int = isinstance( T11_value,int)
            T11_expected = 3
            T12_float = isinstance( T12_value,float)
            T12_expected = 3.4
            T13_list = isinstance( T13_value,list)
            T13_expected = [3,4,]
            T14_dict = isinstance( T14_value,dict)
            T14_expected = {3:4}
            ##T15_none = isinstance( T15_value,None)
            T15_expected = None
            T16_tuple = isinstance( T16_value,tuple)
            T16_expected = (3,4,)
            T17_bool = isinstance( T17_value,bool)
            T17_expected = False
            
            self.assertEqual(T11_value, T11_expected, "T11_Int value should be 3")
            self.assertTrue(T11_int, "T11 is not integer")
            self.assertEqual(T12_value, T12_expected, "T12_Float value should be 3.4")
            self.assertTrue(T11_int, "T12 is not float")
            self.assertEqual(T13_value, T13_expected, "T13_List value should be [3,4,]")
            self.assertTrue(T13_list, "T13 is not list")
            self.assertEqual(T14_value, T14_expected, "T14_Dict value should be {3:4}")
            self.assertTrue(T14_dict, "T14 is not dictionaty")
            
            self.assertEqual(T15_value, T15_expected, "T15_None value should be None")
            ##self.assertTrue(T15_None, "T15 is not None")
            self.assertEqual(T16_value, T16_expected, "T16_Tuple value should be (3,4)")
            self.assertTrue(T16_tuple, "T16 is not tuple")
            self.assertEqual(T17_value, T17_expected, "T17_bool value should be False")
            self.assertTrue(T17_bool, "T17 is not boolena")
        
        def test_input_variable(self):
            #T18 - Test for input variable
            # If input=False expect to over-write original setting (if exists) or define variable
            # If input=True expect not to over-write original setting (if exists) or define variable
            
            input_env = [EnvVar(name='T18_input', cast='integer', value =5, input= False)]
            T18_value = module_env.get('T18_input')
            T18_expected = 3
            self.assertEqual(T18_value, T18_expected, "T18 is not correct - should be taken from projenv of the main env")
            module_env.update_env(input_env)
            T18_value = module_env.get('T18_input')
            T18_expected = 5
            self.assertEqual(T18_value, T18_expected, "T18 is not correct - should be updated by value in input_env")
            
            input_env = [EnvVar(name='T19_input', cast='integer', value =15, input= True)]
            T19_value = module_env.get('T19_input')
            T19_expected = 10
            self.assertEqual(T19_value, T19_expected, "T19 is not correct - should be taken from projenv of the main env")
            module_env.update_env(input_env)
            T19_value = module_env.get('T19_input')
            T19_expected = 10
            self.assertEqual(T19_value, T19_expected, "T19 is not correct - should not be updated by value in input_env")
            
        def test_personalenv(self):
            #Test for variable overwrite in personalenv
            #T20_personal is defined in both projectenv and personalenv
            #We expect personalenv value to be used
            T20_value = module_env.get('T20_personal')
            T20_expected = 51
            self.assertEqual(T20_value, T20_expected, "T20 is not correct - should be taken from personalenv of the main env")
                         
unittest.main()
