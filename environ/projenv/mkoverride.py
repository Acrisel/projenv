#!/usr/bin/env python3

'''
Created on Apr 20, 2015

@author: arnon
'''

import os.path
import os
from string import Template

from .mkproj import mk_ac_env_name, get_personalenv_template, get_accord_loc

def abort(msg):
    print(msg)
    print('Aborting!')
    exit()

def get_proj_loc():
    while True:
        ac_proj_loc=input("Enter project location: ")
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

def personalize(projectloc):
    
    ans=input("Personalize project? [yes]:")
    ans=ans.replace(' ', '').lower()
    ans='yes' if not ans else ans
    
    if ans in ['y', 'yes']:
        # define defaults
        ac_accord_loc=get_accord_loc()
        
        try:
            from projenv.environ import Environ 
        except ImportError as e :
            abort('personalize: import error : {}'.format(repr(e)))
            
        ac_env_name=mk_ac_env_name()
        personalenv_template=get_personalenv_template(ac_accord_loc)
        
        vars={'__AC_TEMPLATE_ENV_NAME__': ac_env_name,}        
        personalenv=Template(personalenv_template).safe_substitute(vars)
        
        personalenv_file=os.path.join(projectloc, 'personalenv.xml')
        
        try:
            with open(personalenv_file, 'w') as file:
                file.write(personalenv)
        except Exception as e:
            abort('Failed to write projectenv {}; {}'.format(personalenv_file, repr(e)))
            
        print('Successfully created projectenv {}'.format(personalenv_file))
    
if __name__ == '__main__':
    projectloc=get_proj_loc()
    personalize(projectloc)       
    from .mkprojlocs import mk_proj_locs
    mk_proj_locs(projectloc)






    
            


