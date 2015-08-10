#!/usr/bin/env python3
'''
Created on Mar 4, 2014

@author: arnon
'''
from .main import Environ
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sandbox", help="path to project sandbox", nargs='?') 
    parser.add_argument("-e", "--env", help="environment variable", nargs="*", metavar='NAME=VALUE') 
    args = parser.parse_args()
    
    environ=Environ(path=args.sandbox)
    environ.load_env()
    
    envvars=[\
          'export {}="{}"'.format(var.name, var.value) for var in environ.main.values() \
          if var.export]
    
    print("\n".join(envvars))