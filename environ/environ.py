'''
Created on Dec 29, 2013

@author: arnon
'''

import os.path
import xml.etree.ElementTree as etree
from collections import OrderedDict
from xml.dom import minidom
from namedlist import namedlist

from . import expandvars
from . import cast_value
from .expandvars import pathhasvars

import logging

logger=logging.getLogger(__name__)

EnvVar=namedlist('EnvVar', 
                 [('name', None),
                  ('value', None),
                  ('override',True),
                  ('input', False),
                  ('cast', 'string'),
                  ('export', False),
                  ('encrypt', ''),
                  ('rest', None),
                  ('origin', None),])

NONE_XML_FIELD=['origin']
DEFAULT_ENVVAR=EnvVar()._asdict()

EnvImport=namedlist('EnvImport', 
                    [('name', None),
                     ('path', None),])

_EnvNode=namedlist('_EnvNode', [('project', None), 
                                ('package', None), 
                                ('personal', None),])

class EnvironError(Exception):
    def __init__(self, msg):
        self.msg=msg
        
    def __repr__(self):
        return repr(self.msg)
    
    def __str__(self):
        return repr(self.msg)
    
DOTPROJECTENV='.projectenv'
PACKAGEENV='packageenv'
PERSONALENV='personalenv'
ENVTAG='environ'

Configure=namedlist('Configure', 
                    [('projectfile', DOTPROJECTENV),
                     ('packagefile', PACKAGEENV),
                     ('personalfile', PERSONALENV),
                     ('xmlenclosure', ENVTAG),
                     ('syntax', 'xml'),])

ENV_SYNTAX_EXT={'xml':'.xml',}

def advise_project_loc(path=None, mark=None):
    ''' Finds root path for project according to a file that 
    would identifies with root path.
        Program will walk upwards directory tree starting with path
        until mark is found.
    
    Args: 
        path: starting node in directory tree. 
        mark: file that identifies project root folder.
        
    Returns:
        (project_location, relative_location) pair where:
        project_location root location (hosting .projectenv.xml)
        relative_location from project_location to program location
    '''
    
    ''' set default project file as xml '''
    if mark is None:
        mark=DOTPROJECTENV + ENV_SYNTAX_EXT['xml']
    
    cwd=os.getcwd() if path is None or path == '' else path
    sandbox=os.path.abspath(cwd) 
    rel_loc=''
    found=False
    stop=False
    
    while not stop and not found:
        conf_file=os.path.join(sandbox, mark)
        if os.path.isfile(conf_file):
            found=True
        else:
            (sandbox, tail)=os.path.split(sandbox)
            if tail != '':
                rel_loc=os.path.join(tail, rel_loc)
            else:
                stop=True
    if found:
        return (sandbox, rel_loc)
    else:
        return (None, None)
    
'''
    End definition of utilities
'''
        
class Environ(object):
    ''' Environ class is Accord way to manage environment variables.
        There are three level of environment files:
            .projectenv.xml is system level Accord project's default environment.
            packageenv.xml is project level overrides and extension. 
            personalenv.xml is 'this' sandbox overrides and extension. 
            <environment> clause in Part overrides and extension.
            
        ground rules when overriding environment variable:
            value can be override only if it is defined as such in parent environment 
            cast can be override although it consistency would be best practices.
            override quality can be only removed by derivative environment; 
            once removed, cannot be added back by derivative environments.
            '''
    
    def __init__(self, osenv=True, configure=None):
        ''' Instantiates Environ object by setting its internal dictionary. 
        Args:
            osenv: if True, inherit os.environ
            
            config: dict of name override to default setting:
               {'.projectenv':'.projectenv',
                'packageenv':'packageenv',
                'personalenv':'personalenv',
                'xmlenclosure':'environ'}
                
        Returns: Environ object filled according to tree environment settings.
        Access environ dictionary directly by its attribute environ.
        '''
        
        self.__config=Configure()
        if configure:
            assert isinstance(configure, dict), \
                    'Environ config argument must be of dict but found {}'.\
                    format(type(configure).__name__)
            self.__config._update(**configure)
        
        self.__syntax=self.__config.syntax
        try:
            self.__ext=ENV_SYNTAX_EXT[self.__syntax]
        except KeyError:
            assert False, 'Failed to find syntax extension, unsupported syntax {}.'.format(self.__syntax)
        self.DOTPROJECTENV=self.__config.projectfile + self.__ext
        self.PACKAGEENV=self.__config.packagefile + self.__ext
        self.PERSONALENV=self.__config.personalfile + self.__ext
        
        ''' Start with empty environment.  Order is important, as environment may
        be defined based on previous values.'''
        self.environ=OrderedDict()
        
        ''' Next load OS environment '''
        if osenv:
            for name, value in os.environ.items():
                self.environ[name]=EnvVar(name=name, value=value, input='True')
                    
    def loads(self, env=None, path=None, envtree=True): 
        ''' Instantiates Environ object by setting its internal dictionary. 
        Args:
            env: lest of EnvVar records to use as overrides.
            path: node path to start with.  Defaults to Current Working Directory.
            envtree: if set will attempt to load environment tree from root location to path
                
        Returns: Environ object filled according to tree environment settings.
        Access environ dictionary directly by its attribute environ.
        '''
        
        if path is not None and envtree:
            if not os.path.exists(path):
                raise EnvironError('Path not found: {}'.format(path))
            self.path=path
            self.__build_env_tree(path=path)
        elif envtree:
            self.path=os.getcwd()
            self.__build_env_tree(path=self.path)
            
        if env is not None:
            env_type =type(env)
            if env_type is list:
                env_items=env
            elif env_type is OrderedDict or env_type is dict:
                env_items=env.values()
            else:
                env_items=None
            for var in env_items:
                self.environ[var.name]=var.value
        return self
        
    def __getitem__(self, key):
        try:
            var=self.environ[key]
        except KeyError:
            raise
        return var.value
    
    def __setitem__(self, key, value):
        self.environ[key]=value
        
    def keys(self):
        return self.environ.keys()
    
    def items(self):
        result=OrderedDict(map(lambda x: (x[0], x[1].value), self.environ.items()))
        return result.items()
    
    def values(self):
        return map(lambda x: x.value, self.environ.values())
    
    def get(self, key):
        var=self.environ.get(key)
        if var is not None:
            value=var.value
        else:
            value=None
        return value   
    
    def __get_root_env(self, file):
        tree=etree.parse(file)
        root=tree.getroot()
        env_root=root.find(self.__config.xmlenclosure)
        return env_root
    
    def __eval_env_schema(self, env_schema):
        ''' evaluate schema; 
            1. converts vars into self.environ 
            2. converts imports to evaluated schemas
            
        Args:
            Ordered Dict of Schema
        '''
        for var in env_schema.values():
            if isinstance(var, EnvVar):
                envvar=EnvVar(**var._asdict())
                envvar.value=expandvars(source=envvar.value,environ=self)
                
                if envvar.export:
                    os.environ[envvar.name]=envvar.value
                
                if envvar.cast is not None:
                    envvar.rest=dict([(n,expandvars(source=v,environ=self)) \
                                      for n,v in envvar.rest.items()])
                    envvar.rest['value']=envvar.value
                    try:
                        envvar.value=cast_value(target_type=envvar.cast,
                                                attrib=envvar.rest)
                        envvar.rest=None
                    except KeyError:
                        msg='Unknown cast: {}; varname {}; origin: {}'\
                            .format(envvar.cast,envvar.name,envvar.origin)
                        raise EnvironError(msg)
                    else:
                        envvar.cast=envvar.cast
                self.environ[envvar.name]=envvar  
            #elif isinstance(var, EnvImport):
            #    ''' Dive into the import '''
            #    env_path=OrderedDict()
            #    path=expandvars(var.path, self)
            #    env_schema=self.__get_env_path(path)
            #    print('Load path: ', path)
            #    self.__print_schema(env_schema)
            #    self.__eval_env_schema(env_schema)              
            else:
                msg='Unknown var type: {}; needs to be EnvVar only'\
                    .format(var.cast, var.name, var.origin)
                raise EnvironError(msg)                          
    
    def __build_env_tree(self, path):
        env_schema=self.__get_env_path(path)
        self.__eval_env_schema(env_schema)
                
    def __get_env_node(self, path):
        ''' get environments files starting from path.
            adds list of import files and convert them to environment schema '''
        #env_var_trees=_EnvTrees()
        #env_import_trees=OrderedDict()
        node_files=_EnvNode()
        if path is not None:
            sys_env_file = os.path.join(path,self.DOTPROJECTENV)
            if  os.path.isfile(sys_env_file):
                node_files.project=sys_env_file
            prj_env_file = os.path.join(path, self.PACKAGEENV)
            if  os.path.isfile(prj_env_file):
                node_files.package=prj_env_file
            lcl_env_file = os.path.join(path, self.PERSONALENV)
            if  os.path.isfile(lcl_env_file):
                node_files.personal=lcl_env_file
            node_env=self.__make_node_schema(node_files)
        return node_env
    
    def __update_var(self, source_map, override):
        name=override.name
        try: 
            current=source_map[name]
        except KeyError:
            source_map[name]=override
        else:
            if current.override:
                source_map[name]=override
            else:
                msg='Trying to override {}; source {}; offender {};'\
                    .format(name, current.origin, override.origin)
                raise EnvironError(msg)
    
    def __update_env_map(self, source_map, override_map):
        if len(source_map) >0:
            for name, var in override_map.items():
                if isinstance(var, EnvVar):
                    self.__update_var(source_map=source_map, override=var) 
                elif isinstance(var, EnvImport):
                    source_map[name]=var
                else:
                    msg='Unknown var type: {}; needs to be EnvVar or EnvImport'\
                        .format(var.cast, var.name, var.origin)                    
        else:
            source_map.update(override_map)         
    
    def __make_node_schema(self, node_files):
        ''' Builds environment dictionary out of node_files.
        personal overrides package which overrides project environment.
        
        Args:
            node_files: EnvNode structure project, package, and personal.
        '''
        env_map=OrderedDict()
        files=filter(lambda f: f is not None, 
                     [node_files.project, node_files.package, node_files.personal])
        for file in files:
            root=self.__get_root_env(file)
            for child in root:
                tag=child.tag.lower()
                if tag == 'var':
                    attrib=child.attrib
                    var=EnvVar(**attrib)
                    var.origin=file
                    self.__update_var(source_map=env_map, override=var) 
                        
                    ''' rest will be set with unused attributes '''
                    var.rest=OrderedDict(set(attrib.items())-set(var._asdict().items()))
                elif tag == 'import':
                    attrib=child.attrib
                    var=EnvImport(**attrib)
                    env_map[var.name]=var           
        return env_map
               
    def __get_env_path(self, path):
        ''' Gets the environment schema representing Path.
        This include fetching all environment nodes from path to its project '''
        mark=self.DOTPROJECTENV
        path=expandvars(path, environ=self)
        env_nodes=list()
        if not pathhasvars(path):
            (project_loc, relative_loc)=advise_project_loc(path=path, mark=mark)
            if relative_loc is not None:
                rel_nodes=os.path.split(relative_loc)
                if project_loc == os.path.abspath(os.sep):
                    raise EnvironError("Project environment file {} doesn't exist for: {}".format(self.DOTPROJECTENV,path))
                start=project_loc
                nodes=[start]
                for node in rel_nodes:
                    start=os.path.join(start, node)
                    nodes.append(start)
                for node in nodes:
                    env_node=self.__get_env_node(path=node)
                    if len(env_node) > 0:
                        env_nodes.append(env_node) 
            else:
                raise EnvironError("Project environment file {} doesn't exist for: {}".format(self.DOTPROJECTENV,path))
        
        ''' Combine all path nodes into single dict - override in order'''
        env_path_raw=OrderedDict()
        for node in env_nodes:
            self.__update_env_map(env_path_raw, node)
            
        env_path=OrderedDict()
        for name, var in env_path_raw.items():
            if not isinstance(var, EnvImport):
                env_path[name]=var
            else:
                path=expandvars(var.path, self)
                env_import=self.__get_env_path(path)
                self.__update_env_map(env_path, env_import) 
                               
        return env_path
    
    def __get_env_map(self, root):
        env_map=OrderedDict()
        import_map=OrderedDict()
        for child in root:
            tag=child.tag.lower()
            if tag == 'var':
                attrib=child.attrib
                try:
                    cast=attrib['cast']
                except KeyError:
                    var=EnvVar(**attrib)
                else:
                    adjusted_attrib=dict(filter(lambda x: x[0] != 'cast', attrib.items()))
                    var=EnvVar(cast=cast, **adjusted_attrib)
                env_map[var.name]=var
                ''' rest will be set with unused attributes '''
                var.rest=OrderedDict(set(attrib.items())-set(var._asdict().items()))
            elif tag == 'import':
                var=EnvImport(**child.attrib)
                import_map[var.name]=var
            
        return import_map, env_map
    
    @classmethod
    def cmd_line_env(cls, env):
        environ=Environ(osenv=False)#.loads(envtree=False)
        if env is not None:
            for item in env:
                parts=item.split('=')
                name=parts[0]
                value='='.join(parts[1:])
                environ.environ[name]=EnvVar(name=name, value=value)
        return environ
    
    def __make_var(self, var, prefix_replace=None, prefix_add=None, prefix_exclusicve=True):
        ''' First try replace, if not done or prefix_exlusive is False, do prefix_add '''
        new_var=None
        if prefix_replace:
            replace_from=prefix_replace[0]
            if var.name.starts_with(replace_from):
                new_var=var.copy()
                replace_to=prefix_replace[1]
                var.name=replace_to+var.name[len(replace_from):]
        if prefix_add and (new_var is None or not prefix_exclusicve):
                new_var=var.copy() if new_var is None else var
                var.name=prefix_add+var.name
        return new_var if new_var is not None else var          
            
    def update_env(self, environ, force_override=False, prefix_replace=None, prefix_add=None, prefix_exclusicve=True): 
        ''' Update override-able environ with values from overrides
            plus adding new vars into environ. 
            The host environment can have two type of parameters.
            1. Regular
            2. Overrideable 
            Regular environment variables are left unchanged.  If it is provided by 
            the suggested environment - a warning will result.
            Overrideable environment variables are changed according to the given environment.
            The given environment may have two types of variables.
            1. Regular
            2. Input.
            
            A regular environment variable will override will override base environment if
            base environment is defined overrideable.
            Input environment parameter will not override the environment one if exist.
            
            If prefix_replace is provided, it is expected to be a tuple (from_prefix, to_prefix).
            In this case, variables names in given environment will be replaced by changing 
            from_prefix into to_prefix
            
            If prefix_add is provided, it is expected to be a string that would be added as prefix 
            to given environ variable names.
            
            prefix_exclusive direct the behavior in case both replace is applicable.  When True, 
            prefix_add will be be done only is prefix_replace is not applicable.
            '''
        if environ is not None:
            env_type=type(environ)
            if env_type is list:
                items=environ
            elif env_type is OrderedDict or env_type is dict:
                items=environ.values()
            else:
                items=list()
            
            for var in items:
                other_var=self.__make_var(var, prefix_replace=None, prefix_add=None, prefix_exclusicve=True)
                try:
                    self_var=self.environ[other_var.name]
                except KeyError:
                    ''' if not found in existing Environ - just update Environ '''
                    if isinstance(other_var.value, str):
                        other_var.value=expandvars(other_var.value, self)
                    self.environ[other_var.name]=other_var
                else:
                    ''' if in Environ, override only if defined as such. '''
                    if self_var.override and not other_var.input or force_override:
                        if isinstance(other_var.value, str):
                            other_var.value=expandvars(other_var.value, self)
                        self.environ[other_var.name]=other_var
                        
                ''' Export to process' Environ if defined as such '''
                if other_var.export:
                    value=other_var.value
                    if not isinstance(value, str):
                        value=str(value)
                    os.environ[other_var.name]=value
        return self
            
    def dup_env(self):
        env={}
        for name, var in self.environ.items():
            env[name]=var.value
        return env
        
    def log_env(self, log=None):
        mylog=print if log is None else log
        msg=map(lambda x: '{k}={v}'.format(k=x, v=self.environ[x].value), 
                sorted(self.environ.keys()))
        mylog('Environ Begin:\n\t'+'\n\t'.join(msg)+'\n\tEnviron End.')
        
    def __clean_env_var(self, var):
        default=DEFAULT_ENVVAR
        if isinstance(var, EnvVar):
            var=var._asdict()
        clean=list(filter(lambda x: x[1] != default[x[0]] and x[0] not in NONE_XML_FIELD, 
                          var.items()))
        return OrderedDict(clean)
        
    def __xml_repr(self, root=None):
        if root is not None:
            env=etree.SubElement(root, self.__config.xmlenclosure)
        else:
            env=etree.Element(self.__config.xmlenclosure)
            root=env
        for key in self.environ.keys():
            attrib=self.environ[key]._asdict()
            try:
                rest=attrib['rest']
            except KeyError:
                pass
            else:
                if rest is not None:
                    attrib.update(rest)
                del attrib['rest']      
            
            attrib=self.__clean_env_var(attrib)
            attrib=OrderedDict(map(lambda x: (x[0], str(x[1])), attrib.items()))    
            el=etree.SubElement(env, 'var', attrib=attrib)
        return root
    
    def __pretty_xml(self, root=None):
        xml=self.__xml_repr(root=root)
        rough_string = etree.tostring(xml, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def dumps(self, env_file=None):
        ''' writes environ structre into file. 
        
        Args:
            env_file: file to which file be written. '''
        xml=etree.Element('{http://www.w3.org/2005/Atom}feed',
                          attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'en'})
        env=etree.SubElement(xml, 'environment')
        xml=self.__pretty_xml(root=env)
        if env_file is not None:
            et=etree.ElementTree(element=xml)
            et.write(env_file) 
        else:
            return xml
            
    def __print_schema(self, schema):
        for n, v in schema.items():
            print('{}={}'.format(n,v))  

    def __repr__(self):
        txt='environ: {\n' #'Environ Begin:\n'
        body=[]
        for key in sorted(self.environ.keys()):
            body.append('\t({key}={value})'.format(key=key, value=self.environ[key].value))
        txt+='\n'.join(body)+'}\n' #'Environ End.\n'
        return txt
    
    def __str__(self):
        return self.__pretty_xml()
    

