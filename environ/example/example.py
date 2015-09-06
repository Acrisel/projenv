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
    ##os.environ['HOME'] = os.environ.get('USERPROFILE','None')
    os.environ['HOME'] = str('C:/Users/uri')
    


logger=logging.getLogger('Example')

handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

input_environ=[EnvVar(name='A1',value='133', input=True),]

root_loc=os.path.dirname(__file__)
module_loc=os.path.join(root_loc, 'envexample', 'lvl1', 'lvl2', 'lvl3')
module_env=Environ(osenv=True, trace_env=['A1', ], logclass='Example') #, ulogger=logger)
module_env.loads(path=module_loc)
module_env.update_env(input_environ=input_environ)

print('POST ENVIRON:', repr(module_env))

import pickle

pickle.dumps(module_env)
