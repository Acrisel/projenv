#!/usr/bin/env python3

'''
Created on Apr 20, 2015

@author: arnon
'''

import os.path
import os
from string import Template
import argparse

user_home=os.path.expanduser('~')

def abort(msg):
    print(msg)
    print('Aborting!')
    exit()
    
def mk_ws_loc(args, proj_name):
    global user_name

    if not args.workspace_loc:
        try:
            ws_loc_def=os.environ['AC_WS_LOC']
        except KeyError:
            ws_loc_def=os.path.join(user_home, 'accords','sand')
    else:
        ws_loc_def=args.workspace_loc
        
    ws_loc=''
    while not ws_loc:
        ws_loc=get_key(default=ws_loc_def, title="location for project's source folder (AC_WS_LOC)")
        proj_loc=os.path.join(ws_loc, proj_name)
        try:
            os.makedirs(proj_loc)
        except FileExistsError as e:
            print("Project location {} already exists.".format(proj_loc))
            ans=input("Continue anyway? [No]: ")
            ans='no' if not ans else ans.lower()
            if ans in ['n', 'no']:
                continue
        except OSError as e:
            abort("Failed to create project location {}".\
                  format(proj_loc), repr(e))
        else:
            print("Project location {} created.".format(proj_loc))  
    if not ws_loc.endswith('/'):
        ws_loc +='/'
    return ws_loc

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

def get_key(title, default=''):   
    result=''
    while not result:
        show_default=' [{}]'.format(default) if default else ''
        in_keys=input("Enter {}{}: ".format(title, show_default))
        in_keys=in_keys.strip()
        if in_keys.replace(' ', '') == in_keys:
            result=in_keys
        elif in_keys:
            print('Your entry must not include whitespace.')
        if not result:
            # default was chosen
            result=default
    return result

def mk_proj_prefix(args):
    if not args.project_prefix:
        default=os.environ.get('AC_PROJ_PREFIX')
        if not default:
            default='AC_'
        result=get_key(default=default, title='project prefix (AC_PROJ_PREFIX)')
    else:
        result=args.project_prefix
    return result

def mk_vs_area(args, proj_name):
    if not args.dataspace_loc:
        try:
            ac_vs_def=os.environ['AC_DATA_LOC']
        except KeyError:
            ac_vs_def=os.path.join(user_home, 'accords', 'data')
    else:
        ac_vs_def=args.dataspace_loc
    
    #ac_var_default=os.path.join(ac_vs_loc, proj_name) 
    
    #if not args.data_loc:
    while True:
        ac_vs=get_key(default=ac_vs_def, title="location for project's var folder (AC_VS_LOC)")
        ac_var=os.path.join(ac_vs, proj_name) 
        if not os.path.exists(ac_var):
            ans=input("Var space location {} don't exist, create? [Yes]: ".format(ac_var))
            ans='yes' if not ans else ans.lower()
            if ans in ['n', 'no']: continue
            try: # YES
                os.makedirs(ac_var, exist_ok=True)
            except OSError as e:
                msg="Failed to create {}; cleaning up; {}".\
                      format(ac_var, repr(e))
                abort(msg)
        break

    if not ac_vs.endswith(os.path.sep):
        ac_vs +=os.path.sep      
    return ac_vs    

def get_projectenv_template(ac_accord_loc):
    template_file=os.path.join(ac_accord_loc,'bin','projectenv_template.xml')
    try:
        with open(template_file, 'r') as content_file:
            project_template=content_file.read()
    except Exception as e:
        msg='Failed to read template file {}; {}'.format(template_file, repr(e))
        abort(msg)
    return project_template

def get_personalenv_template(ac_accord_loc):
    template_file=os.path.join(ac_accord_loc,'bin','personalenv_template.xml')
    try:
        with open(template_file, 'r') as content_file:
            project_template=content_file.read()
    except Exception as e:
        msg='Failed to read template file {}; {}'.format(template_file, repr(e))
        abort(msg)
    return project_template

def get_accord_loc(loc=None):
    if not loc:
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
    else:
        ac_accord_loc=loc
    return ac_accord_loc

def mk_ac_env_name(args):
    if not args.environment_name:
        in_env_name=input("Enter environment name [.]: ")
        env_name=in_env_name.replace(' ','')
        env_name='.' if not env_name else env_name.lower()
    else:
        env_name=args.environment_name
    return env_name

def get_proj_prefix(proj_loc):
    try:
        import aclib.environ as environ 
    except ImportError as e:
        abort('get_proj_prefix: import error : {}'.format(repr(e)))   
        
    env=environ.Environ().loads(path=proj_loc)
    
    prefix=env.get('AC_PROJ_PREFIX')
    if not prefix:
        abort('Project environment does not include AC_PROJ_PREFIX.  Please check project {} environment.'.format(proj_loc))

    return prefix

def mk_project(args):
    ''' 
    ac_ws_loc:
        default: AC_WS_LOC
                 os.path.join(user_home, 'accords','sand')
                 
    ac_proj_name:
        default: no defaults
        
    ac_var_area:
        default: AC_DATA_LOC
                 os.path.join(user_home, 'accords', 'data')
                 
    ac_proj_prefix:
        default: AC_

'''
    ac_accord_loc=get_accord_loc(loc=args.accord_loc)   
    
    if not args.project_name:
        ac_proj_name=get_key(title='project name (name of folder that will be created for project)')
    else:
        ac_proj_name=args.project_name
        
    ac_ws_loc=mk_ws_loc(args=args, proj_name=ac_proj_name)
    ac_proj_loc=os.path.join(ac_ws_loc,ac_proj_name)
    if not args.personal_only:
        ac_vs_loc=mk_vs_area(args=args, proj_name=ac_proj_name)
        ac_proj_prefix=mk_proj_prefix(args=args)
    else:
        ac_vs_loc=None
        if not args.args.project_prefix:
            ac_proj_prefix=get_proj_prefix(ac_proj_loc)
        else:
            ac_proj_prefix=args.args.project_prefix
    ac_env_name=mk_ac_env_name(args=args)

    vars={'__AC_TEMPLATE_WS_LOC__': ac_ws_loc,
          '__AC_TEMPLATE_PROJ_NAME__':ac_proj_name,
          '__AC_TEMPLATE_VS_LOC__':ac_vs_loc,
          '__AC_TEMPLATE_PREFIX__':ac_proj_prefix,
          '__AC_TEMPLATE_ENV_NAME__': ac_env_name,}
    
    #projectloc=os.path.join(ac_proj_loc, ac_proj_name)

    projectenv_template=get_projectenv_template(ac_accord_loc)
    projectenv=Template(projectenv_template).safe_substitute(vars)
    projectenv_file=os.path.join(ac_proj_loc, '.projectenv.xml')       
    try:
        with open(projectenv_file, 'w') as file:
            file.write(projectenv)
    except Exception as e:
        abort('Failed to write projectenv {}; {}'.format(projectenv_file, repr(e)))        
    print('Successfully created projectenv {}'.format(projectenv_file))
    
    personalenv_template=get_personalenv_template(ac_accord_loc)
    personalenv=Template(personalenv_template).safe_substitute(vars)
    personalenv_file=os.path.join(ac_proj_loc, 'personalenv.xml')
    try:
        with open(personalenv_file, 'w') as file:
            file.write(personalenv)
    except Exception as e:
        abort('Failed to write projectenv {}; {}'.format(personalenv_file, repr(e)))            
    print('Successfully created projectenv {}'.format(personalenv_file))

    return ac_proj_loc
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()

    parser.add_argument('-a', '--accord_loc', help='location of accord package', type=str, nargs='?', metavar='AC_ACCORD_LOC')
    parser.add_argument('-p', '--project_name', help='name of project', type=str, nargs='?', metavar='NAME')
    parser.add_argument('-w', '--workspace_loc', help='location of workspace where sandbox are created', type=str, nargs='?', metavar='AC_WS_LOC')
    #parser.add_argument('-s', '--source_loc', help='location of source code workspace', type=str, nargs='?', metavar='PATH')
    parser.add_argument('-d', '--dataspace_loc', help='location of data space where data projects are created', type=str, nargs='?', metavar='AC_DATA_LOC')
    #parser.add_argument('-d', '--data_loc', help='location of data workspace', type=str, nargs='?', metavar='PATH')
    parser.add_argument('-f', '--project_prefix', help='project prefix ', type=str, nargs='?', metavar='AC_PROJ_PREFIX')
    parser.add_argument('-e', '--environment_name', help='name of environment personalization', type=str, nargs='?', metavar='NAME')
    parser.add_argument('-o', '--personal_only', help='personalize only', action='store_true')

    args = parser.parse_args()
    
    projectloc=mk_project(args)
    from accord.bin.mkprojlocs import mk_proj_locs
    mk_proj_locs(projectloc)







    
            


