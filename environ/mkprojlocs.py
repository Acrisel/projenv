#!/usr/bin/env python3

'''
Created on Apr 20, 2015

@author: arnon
'''

import os.path
import os
from string import Template

def abort(msg):
    print(msg)
    print('Aborting!')
    exit()

def mk_proj_loc():
    while True:
        ac_proj_loc=input("Enter project sand-box location: ")
        ac_proj_loc=ac_proj_loc.replace(' ','')
        if not ac_proj_loc:
            print('Your entry must not include whitespace.')
            continue
        if not os.path.exists(ac_proj_loc):
            ans=input("Project location entered don't exist, must provide existing project")
            continue
        else:
            projectenv=os.path.join(ac_proj_loc, '.projectev.xml')
            if os.path.exists(projectenv):
                break
        continue
    return ac_proj_loc    
    
def mk_proj_locs(projectloc):
    
    try:
        from aclib.environ import Environ 
    except ImportError:
        abort('aclib is not installed or not on PYTHONPATH')   

    ans=input("create project locations? [yes]:")
    ans=ans.replace(' ', '').lower()
    ans='yes' if not ans else ans
    if ans in ['y', 'yes']:
        print('Creating project locations:')   
        env=Environ().loads(path=projectloc)
        items=env.items()
        for n,v  in items:
            if n.startswith('AC_') and n.endswith('_LOC'):
                if not os.path.exists(v):
                    try:
                        os.makedirs(v)
                    except OSError as e:
                        print('    {}: Failed to create {}; {}'.format(n,v, repr(e)))
                    else:
                        print('    {}: Created {}'.format(n,v))
                else:
                    print('    {}: Already exists {}'.format(n,v))

if __name__ == '__main__':
    
    projectloc=mk_proj_loc()
    mk_proj_locs(projectloc)





    
            


