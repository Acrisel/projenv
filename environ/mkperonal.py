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

def mk_ac_env_name():
    in_env_name=input("Enter environment name [.]: ")
    env_name=in_env_name.replace(' ','')
    env_name='.' if not env_name else env_name.lower()
    return env_name


def get_personalenv_template(ac_accord_loc):
    template_file=os.path.join(ac_accord_loc,'bin','personalenv_template.xml')
    try:
        with open(template_file, 'r') as content_file:
            project_template=content_file.read()
    except Exception as e:
        msg='Failed to read template file {}; {}'.format(template_file, repr(e))
        abort(msg)
    return project_template

def personalize(projectloc):
    
    ans=input("Personalize project? [yes]:")
    ans=ans.replace(' ', '').lower()
    ans='yes' if not ans else ans
    if ans in ['y', 'yes']:
        # define defaults
        try:
            ac_accord_loc=os.environ['AC_ACCORD_LOC']
        except KeyError:
            import accord
            try:
                ac_accord_loc=accord.__path__[0]
            except AttributeError:
                try:
                    file=accord.__file__
                except AttributeError:
                    msg=['Cannot find accord installation, please install accord.',
                         '    please install accrod,',
                         '    define AC_ACCORD_LOC, and',
                         '    add it PYTHONPATH.',
                         ]
                    abort('\n'.join(msg))    
                       
                else:
                    ac_accord_loc=os.path.dirname(file)
        
        try:
            from aclib.environ import Environ 
        except ImportError:
            abort('aclib is not installed or not on PYTHONPATH')
            
        ac_env_name=mk_ac_env_name()
        personalenv_template=get_personalenv_template(ac_accord_loc)
        
        vars={'_TAMPLATE_AC_ENV_NAME': ac_env_name,}        
        personalenv=Template(personalenv_template).safe_substitute(vars)
        
        personalenv_file=os.path.join(projectloc, 'personalenv.xml')
        
        try:
            with open(personalenv_file, 'w') as file:
                file.write(personalenv)
        except Exception as e:
            abort('Failed to write projectenv {}; {}'.format(personalenv_file, repr(e)))
            
        print('Successfully created projectenv {}'.format(personalenv_file))
    
if __name__ == '__main__':
    projectloc=mk_proj_loc()
    personalize(projectloc)       
    from accord.bin.mkprojlocs import mk_proj_locs
    mk_proj_locs(projectloc)






    
            


