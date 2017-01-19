'''
Created on Jun 15, 2015

@author: arnon
'''

from projenv import Environ, EnvVar
import os.path
import logging

# Ensure variable is defined
x = os.environ.get('HOME','None')

if x is 'None':
    os.environ['HOME'] = str('C:/Users/my_home_path')
    
logger=logging.getLogger('Example')

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

input_environ=[EnvVar(name='A1',value='133', input=True),]

root_loc=os.path.dirname(__file__)

loc=[root_loc, 'penv1', 'lvl1', 'lvl2', 'lvl3',]
module_loc=os.path.join(*loc)
module_env=Environ(osenv=True, trace_env=['A1', 'X1', ], logclass='Example') #, ulogger=logger)
module_env.loads(path=module_loc)
module_env.updates(input_environ=input_environ)

loc=[root_loc, 'penv2', 'lvl1', 'lvl2', 'lvl3',]
module_loc=os.path.join(*loc)
module_env=Environ(osenv=True, trace_env=['A1', 'X1', 'PENV1_LOC'], logclass='Example') #, ulogger=logger)
module_env.loads(path=module_loc)
module_env.updates(input_environ=input_environ)

print('getting', module_env.get('A1'), module_env.get('AA', 'Not found'))
try:
    print(module_env.get('AA'))
except:
    print('failed to get("AA")')

#print('POST ENVIRON:', repr(module_env))
module_env.log_env()

import pickle
pickle.dumps(module_env)
