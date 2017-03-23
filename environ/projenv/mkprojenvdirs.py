#!/usr/bin/env python3

'''
Created on Apr 20, 2015

@author: arnon
'''

import os
import argparse
from projenv.main import Environ  
from projenv.common import PROJENV_PREFIX, get_proenv_prefix

def abort(msg):
    print(msg)
    print('Aborting!')
    exit()

def get_proj_loc(args):
    if not args.source_loc:
        while True:
            proj_loc=input("Enter project location: ")
            proj_loc=proj_loc.replace(' ','')
            if not proj_loc:
                print('Your entry must not include whitespace.')
                continue
            if not os.path.exists(proj_loc):
                ans=input("Project location entered don't exist, must provide existing project")
                continue
            else:
                projectenv=os.path.join(proj_loc, '.envpackage.xml')
                if os.path.exists(projectenv):
                    break
            continue
    else:
        proj_loc=args.source_loc
    return proj_loc 

def check_var_has_value(env, varname):
    value=env.get(varname)
    value=value.strip()
    if not value:
        abort('environment parameter %s is not define or does not have value. check you .envoverride.xml'.format(varname, projectloc))
       
    
def mk_proj_locs(projectloc):

    ans=input("create project folders? [Yes]: ")
    ans=ans.replace(' ', '').lower()
    ans='yes' if not ans else ans
    if ans in ['y', 'yes']:
        print('Creating project folders:')   
        env=Environ().loads(path=projectloc)
        prefix=prefix=env.get(PROJENV_PREFIX)
        if prefix is None:
            abort('Failed to find environment variable {}; should have been found in {}.projectenv.xml'.format(PROJENV_PREFIX, projectloc))
            
        check_var_has_value(env, "%sPROJ_LOC" % prefix)
        check_var_has_value(env, "%sVAR_LOC" % prefix)
        items=env.items()
        for n,v  in items:
            if n.startswith(prefix) and n.endswith('_LOC'):
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
    parser=argparse.ArgumentParser()
    
    pwd=os.getcwd()
    
    parser.add_argument('-p', '--project', type=str, metavar='PATH', default=pwd,
                        help='path to project. defaults to current working directory', )
    args = parser.parse_args()
    
    projectloc=os.path.abspath(args.project)
    mk_proj_locs(projectloc)





    
            


