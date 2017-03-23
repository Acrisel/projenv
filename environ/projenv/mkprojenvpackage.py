#!/usr/bin/env python3

'''
Created on Apr 20, 2015

@author: arnon
'''

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

    if not args.work:
        ws_loc_def=os.path.join(user_home, 'accords','sand')
    else:
        ws_loc_def=args.work
        
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

def get_key(title, default=None):   
    result=None
    while result is None:
        show_default=' [{}]'.format(default) if default is not None else ''
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

def mk_proj_prefix(project, prefix, force_defaults):
    prefix=args.prefix
    if not prefix:
        prefix="%s_" % project.upper()
        if not force_defaults:
            prefix=get_key( title='project prefix', default=prefix)
    return prefix

def mk_vs_area(args, proj_name):
    if not args.data:
        vs_def=os.path.join('/var','data', proj_name)
    else:
        vs_def=args.data
    
    #ac_var_default=os.path.join(ac_vs_loc, proj_name) 
    
    #if not args.data_loc:
    while True:
        var=get_key(default=vs_def, title="location for project's var folder")
        #ac_var=os.path.join(ac_vs) 
        if not os.path.exists(var):
            ans=input("Var space location {} don't exist, create? [Yes]: ".format(var))
            ans='yes' if not ans else ans.lower()
            if ans in ['n', 'no']: continue
            try: # YES
                os.makedirs(var, exist_ok=True)
            except OSError as e:
                msg="Failed to create {}; cleaning up; {}".\
                      format(var, repr(e))
                abort(msg)
        break

    if not var.endswith(os.sep):
        var +=os.path.sep      
    return var    

def get_projectenv_template(template_loc):
    template_file=os.path.join(template_loc,'projenv_template_envpackage.xml')
    try:
        with open(template_file, 'r') as content_file:
            project_template=content_file.read()
    except Exception as e:
        msg='Failed to read template file {}; {}'.format(template_file, repr(e))
        abort(msg)
    return project_template

def get_personalenv_template(template_loc):
    template_file=os.path.join(template_loc,'projenv_template_envoverride.xml')
    try:
        with open(template_file, 'r') as content_file:
            project_template=content_file.read()
    except Exception as e:
        msg='Failed to read template file {}; {}'.format(template_file, repr(e))
        abort(msg)
    return project_template

def get_template_loc(loc=None):   
    if not loc:
        try:
            this_loc=os.path.dirname(__file__)
        except:
            msg=['Cannot find package installation.',]
            abort('\n'.join(msg))    
    else:
        this_loc=loc
    return this_loc

def mk_env_name(environment, force_defaults):
    if not environment:
        environment='.'
        if not force_defaults:
            environment=get_key( title='environment name', default=environment)
    return environment

    '''
    if not environment:
        in_env_name=input("Enter environment name [.]: ")
        env_name=in_env_name.replace(' ','')
        env_name='.' if not env_name else env_name.lower()
    else:
        env_name=environment
    return env_name
        '''

#def get_proj_prefix(proj_loc):
#    try:
#        import projenv.environ as environ 
#    except ImportError as e:
#        abort('get_proj_prefix: import error : {}'.format(repr(e)))   
#        
#    env=environ.Environ().loads(path=proj_loc)
#    
#    prefix=env.get('AC_PROJ_PREFIX')
#    if not prefix:
#        abort('Project environment does not include AC_PROJ_PREFIX.  Please check project {} environment.'.format(proj_loc))
#
#    return prefix

def mk_overrides(template_loc, envvars, envoverride_file):
    personalenv_template=get_personalenv_template(template_loc)
    personalenv=Template(personalenv_template).safe_substitute(envvars)
    try:
        with open(envoverride_file, 'w') as file:
            file.write(personalenv)
    except Exception as e:
        abort('Failed to write projectenv {}; {}'.format(envoverride_file, repr(e)))            

def get_projenv_files(proj_loc):
    envpackage_file=os.path.join(proj_loc, '.envpackage.xml')
    envoverride_file=os.path.join(proj_loc, '.envoverride.xml')
    return envpackage_file, envoverride_file
    
def mk_project(args):
    template_loc=get_template_loc(args.templates)
    
    proj_loc=os.path.abspath(args.project)
    envpackage_file, envoverride_file=get_projenv_files(proj_loc)
    
    # if package file already there, and it is intent to rebuild,
    # validate with user that this is the intention before rebuilding.
    if (os.path.isfile(envpackage_file) and args.skip_override):
        pass
    
    if not args.name:
        name=os.path.basename( proj_loc )
        if not args.force_defaults:
            name=get_key(default=name, title='project name (name of folder that will be created for project)')
    
    if not args.force_defaults:
        proj_version=get_key("project version", default=args.version)
        
    envvars={'__TEMPLATE_PROJ_LOC__': proj_loc,
             '__TEMPLATE_PROJ_NAME__':name,
             '__TEMPLATE_VERSION__':  proj_version, 
             }

    vs_loc=mk_vs_area(args=args, proj_name=name)
    envvars.update({'__TEMPLATE_VAR_LOC__':vs_loc,})

    proj_prefix=mk_proj_prefix(project=name, prefix=args.prefix, force_defaults=args.force_defaults)
    env_name=mk_env_name(environment=args.environment, force_defaults=args.force_defaults)

    envvars.update({'__TEMPLATE_PREFIX__':proj_prefix,
                    '__TEMPLATE_ENV_NAME__': env_name,})
    
    
    #projectloc=os.path.join(ac_proj_loc, ac_proj_name)

    projectenv_template=get_projectenv_template(template_loc)
    projectenv=Template(projectenv_template).safe_substitute(envvars)
               
    try:
        with open(envpackage_file, 'w') as file:
            file.write(projectenv)
    except Exception as e:
        abort('Failed to write projectenv {}; {}'.format(envpackage_file, repr(e)))        
    print('Successfully created projectenv {}'.format(envpackage_file))
    
    if not args.skip_override:
        mk_overrides(template_loc, envvars, envoverride_file)            
        print('Successfully created projectenv {}'.format(envoverride_file))

    return proj_loc
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    
    pwd=os.getcwd()
    
    parser.add_argument('-t', '--templates', type=str, metavar='PATH', default=None,
                        help='location of templates. defaults to projenv built-in templates',)
    parser.add_argument('-p', '--project', type=str, metavar='PATH', default=pwd,
                        help='path to project. defaults to current working directory', )
    parser.add_argument('-n', '--name', type=str, metavar='NAME', default=None,
                        help='name to project. default for directory name of project location', )
    #parser.add_argument('-w', '--codespace', help='location of code space where sandbox are created', type=str, nargs='?', metavar='CODESPACE')
    #parser.add_argument('-s', '--source_loc', help='location of source code workspace', type=str, nargs='?', metavar='PATH')
    parser.add_argument('-d', '--data', type=str, metavar='PATH', default='',
                        help='location of data space where data projects are created, default /var/data/(name of PROJECT)', )
    parser.add_argument('-w', '--work', type=str, metavar='PATH',default='',
                        help='location of work space where processing in-work data is created, default DATA space')
    #parser.add_argument('-d', '--data_loc', help='location of data workspace', type=str, nargs='?', metavar='PATH')
    parser.add_argument('-x', '--prefix', type=str, metavar='NAME', default='',
                        help='project prefix used for environment parameters names. defaults to project name.', )
    parser.add_argument('-e', '--environment', type=str, metavar='NAME', default='',
                        help='name to be use to personalize var area.  Recommended to use when multiple users use the same var area', )
    parser.add_argument('-v', '--version', type=str, metavar='VERSION', default='',
                        help='version for this project environment. Use if need to bind environment version to project.', )
    parser.add_argument('--no-override', action='store_true', default=False, dest='skip_override',
                        help='skips creation of .envoverride.xml', )
    parser.add_argument('--force-defaults', action='store_true', default=False, dest='force_defaults',
                        help='forces the use of default. this option skips interaction', )

    args = parser.parse_args()
        
    projectloc=mk_project(args)
    from projenv.mkprojenvdirs import mk_proj_locs
    mk_proj_locs(projectloc)







    
            


