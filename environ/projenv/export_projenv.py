#!/usr/bin/env python3
'''
Created on Mar 4, 2014

@author: arnon
'''

from projenv.common import get_environ
    
def get_shell_exports(environ, shell='sh'):
    sh='export {}=\"{}\"'
    shell_fmts={
        'sh': sh,
        'bash': sh,
        'ksh;': sh,
        }
    
    fmt=shell_fmts.get(shell, sh)
    envvars=[fmt.format(var.name, var.value) for var in environ.environ.values() \
             if var.export]  
    return envvars

if __name__ == '__main__':
    import argparse
    import os
    
    pwd=os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", type=str, metavar='PATH', default=pwd,
                        help='path to project. defaults to current working directory', )
    #parser.add_argument("-e", "--env", help="environment variable", nargs="*", metavar='NAME=VALUE') 
    parser.add_argument('--shell', choices=['sh', 'ksh', 'bash'], default='sh',
                        help='bind the shell to be compatible with')
    parser.add_argument("--exclude-os", help="does not add OS environ", action='store_true', default=False, dest='exclude_os') 
    args = parser.parse_args()
    
    environ=get_environ(path=args.project, osenv=not args.exclude_os)
    
    envvars=get_shell_exports(environ, args.shell)
    
    print("\n".join(envvars))