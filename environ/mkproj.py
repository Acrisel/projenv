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
    
def mk_ws_loc(ac_ws_loc):
    while True:
        raw_ac_ws_loc=input("Enter project sand-box workspace location [{}]: "\
                           .format(ac_ws_loc))
        in_ac_ws_loc=raw_ac_ws_loc.replace(' ','')
        if in_ac_ws_loc != raw_ac_ws_loc and not in_ac_ws_loc:
            print('Your entry must not include whitespace.')
            continue
        if not in_ac_ws_loc:
            in_ac_ws_loc=ac_ws_loc
            break
        if not os.path.exists(in_ac_ws_loc):
            ans=input("Workspace location entered don't exist, create? [yes]:")
            ans=ans.replace(' ','')
            ans='yes' if not ans else ans.lower()
            if ans in ['y', 'yes']:
                try:
                    os.makedirs(in_ac_ws_loc, exist_ok=True)
                except OSError as e:
                    abort("Failed to create {}; cleaning up; {}".\
                          format(in_ac_ws_loc, repr(e)))
        break            
    return in_ac_ws_loc

def mk_proj_name(ac_ws_loc):
    while True:
        in_proj_name=input("Enter project name: ")
        proj_name=in_proj_name.replace(' ','')
        if not proj_name or in_proj_name != proj_name:
            print('Your entry must not include whitespace.')
            continue
        proj_loc=os.path.join(ac_ws_loc, proj_name)
        try:
            os.makedirs(proj_loc)
        except FileExistsError as e:
            print("Project location already exists {}".\
                  format(proj_loc))
            ans=input("Continue anyway? [No]: ")
            ans='no' if not ans else ans.lower()
            if ans in ['n', 'no']:
                continue
        except OSError as e:
            abort("Failed to create project location {}".\
                  format(proj_loc), repr(e))
        break
    return proj_name    

def mk_var_area(ac_data_loc, ac_proj_name):
    
    ac_var_base=os.path.join(ac_data_loc, ac_proj_name) 
    while True:
        raw_ac_var_base=input("Enter data var-space location [{}]: ".format(ac_var_base))
        in_ac_var_base=raw_ac_var_base.replace(' ', '')
        if in_ac_var_base != raw_ac_var_base and not in_ac_var_base:
            print('Your entry must not include whitespace.')
        if not in_ac_var_base:
            in_ac_var_base=ac_var_base
            break
        if not os.path.exists(in_ac_var_base):
            ans=input("Work space location entered don't exist, create? [yes]:")
            ans='yes' if not ans else ans.lower()
            if ans in ['y', 'yes']:
                try:
                    os.makedirs(in_ac_var_base, exist_ok=True)
                except OSError as e:
                    msg="Failed to create {}; cleaning up; {}".\
                          format(in_ac_var_base, repr(e))
                    abort(msg)
                break
        continue
    return in_ac_var_base    

def get_projectenv_template(ac_accord_loc):
    template_file=os.path.join(ac_accord_loc,'bin','projectenv_template.xml')
    try:
        with open(template_file, 'r') as content_file:
            project_template=content_file.read()
    except Exception as e:
        msg='Failed to read template file {}; {}'.format(template_file, repr(e))
        abort(msg)
    return project_template

def mk_project():
    # define defaults
    user_home=os.path.expanduser('~')
    
    try:
        ac_ws_loc=os.environ['AC_WS_LOC']
    except KeyError:
        ac_ws_loc=os.path.join(user_home, 'accords','sand')
        
    try:
        ac_data_loc=os.environ['AC_DATA_LOC']
    except KeyError:
        ac_data_loc=os.path.join(user_home, 'accords', 'data')
        
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
        
    ac_ws_loc=mk_ws_loc(ac_ws_loc)
    ac_proj_name=mk_proj_name(ac_ws_loc)
    ac_var_area=mk_var_area(ac_data_loc, ac_proj_name)
    projectenv_template=get_projectenv_template(ac_accord_loc)
    
    vars={'_TEMPLATE_AC_WS_LOC': ac_ws_loc,
          '_TEMPLATE_AC_PROJ_NAME':ac_proj_name,
          '_TEMPLATE_AC_VAR_BASE':ac_var_area,}
    
    projectenv=Template(projectenv_template).safe_substitute(vars)
    
    projectloc=os.path.join(ac_ws_loc, ac_proj_name)
    projectenv_file=os.path.join(projectloc, '.projectenv.xml')
    
    try:
        with open(projectenv_file, 'w') as file:
            file.write(projectenv)
    except Exception as e:
        abort('Failed to write projectenv {}; {}'.format(projectenv_file, repr(e)))
        
    print('Successfully created projectenv {}'.format(projectenv_file))
    return projectloc
    
if __name__ == '__main__':
    projectloc=mk_project()
    from accord.bin.mkperonal import personalize
    personalize(projectloc)    
    from accord.bin.mkprojlocs import mk_proj_locs
    mk_proj_locs(projectloc)







    
            


