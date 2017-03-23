#!/usr/bin/env python3

'''
Created on Apr 20, 2015

@author: arnon
'''

import os.path
from projenv.mkprojenvpackage import mk_overrides, get_template_loc, get_projenv_files, mk_env_name
from projenv.main import Environ
from projenv.common import PROJENV_PREFIX
        
def mkoverrides(args):
    template_loc=get_template_loc(args.templates)
    proj_loc=os.path.abspath(args.project)
    _, envoverride_file=get_projenv_files(proj_loc)
    env_name=mk_env_name(environment=args.environment, force_defaults=args.force_defaults)
    env=Environ().loads(path=proj_loc)
    proj_prefix=prefix=env.get(PROJENV_PREFIX)
    
    envvars={'__TEMPLATE_PREFIX__':proj_prefix,
             '__TEMPLATE_PROJ_LOC__': proj_loc,
             '__TEMPLATE_ENV_NAME__': env_name,}

    mk_overrides(template_loc, envvars, envoverride_file) 
    return proj_loc
    
if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    
    pwd=os.getcwd()
    
    parser.add_argument('-t', '--templates', type=str, metavar='PATH', default=None,
                        help='location of templates. defaults to projenv built-in templates',)
    parser.add_argument('-p', '--project', type=str, metavar='PATH', default=pwd,
                        help='path to project. defaults to current working directory', )
    parser.add_argument('-e', '--environment', type=str, metavar='NAME', default='',
                        help='name to be use to personalize var area.  Recommended to use when multiple users use the same var area', )
    parser.add_argument('--force-defaults', action='store_true', default=False, dest='force_defaults',
                        help='forces the use of default. this option skips interaction', )
    args = parser.parse_args()
    
    projectloc=mkoverrides(args)
    from projenv.mkprojenvdirs import mk_proj_locs
    mk_proj_locs(projectloc)






    
            


