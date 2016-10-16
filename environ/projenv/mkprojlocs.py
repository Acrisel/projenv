#!/usr/bin/env python3

'''
Created on Apr 20, 2015

@author: arnon
'''

import os
from string import Template
import argparse
from .projenv import Environ  

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
    
def mk_proj_locs(projectloc):

    ans=input("create project locations? [Yes]: ")
    ans=ans.replace(' ', '').lower()
    ans='yes' if not ans else ans
    if ans in ['y', 'yes']:
        print('Creating project locations:')   
        env=Environ().loads(path=projectloc)
        try:
            prefix=env['PROJ_PREFIX']
        except KeyError:
            abort('Failed to find environment variable AC_PROJ_PREFIX; should have been found in {}.projectenv.xml'.format(projectloc))
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

    parser.add_argument('-s', '--source_loc', help='location of source code workspace', type=str, nargs='?', metavar='PATH')

    args = parser.parse_args()
    
    projectloc=get_proj_loc(args)
    mk_proj_locs(projectloc)





    
            


