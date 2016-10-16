'''
Created on Dec 29, 2013

@author: arnon
'''

import os.path
import xml.etree.ElementTree as etree
from collections import OrderedDict
from xml.dom import minidom
from namedlist import namedlist
import logging
from copy import copy, deepcopy
import ast
import inspect
import sys
import collections

envlogger=logging.getLogger(__name__)

from .expandvars import expandvars
from .expandvars import pathhasvars
from .cast_value import cast_value

EnvVar=namedlist('EnvVar', 
                 [('name', None),
                  ('value', None),
                  ('virtual', False),
                  ('override',True),
                  ('input', False),
                  ('cast', 'string'),
                  ('export', True),
                  ('encrypt', ''),
                  ('rest', None),
                  ('comment', None),
                  ('origin', None),])

NONE_XML_FIELD=['origin']
DEFAULT_ENVVAR=EnvVar()._asdict()

EnvImport=namedlist('EnvImport', 
                    [('name', None),
                     ('path', None),
                     ('comment', None),])

class EnvironError(Exception):
    def __init__(self, msg):
        self.msg=msg
        
    def __repr__(self):
        return repr(self.msg)
    
    def __str__(self):
        return repr(self.msg)


ENV_CONFIG_FILE=".envconfig.xml"

CONFIGURE={ 
    "envnodes": ['.envpackage.xml', '.envoverride.xml'],
    "enclosure" : 'environ',
    'syntax': 'xml',
    'lineage': False,
    
    }


def add_ext(filename):
    return filename # + ENV_SYNTAX_EXT[Configure['syntax']]

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
    #if mark is None:
    #    mark=add_ext(DOTPROJECTENV)
    
    cwd=os.getcwd() if path is None or path == '' else path
    last_sandbox=os.path.abspath(cwd) 
    last_rel_loc=''
    next_sandbox=last_sandbox 
    next_rel_loc=''
    found=False
    #stop=False
    
    while True: # and not found:
        conf_file=os.path.join(next_sandbox, '__init__.py')
        if not os.path.isfile(conf_file): break
        
        found=True
        last_sandbox=next_sandbox
        last_rel_loc=next_rel_loc
        (next_sandbox, tail)=os.path.split(last_sandbox)
        next_rel_loc=os.path.join(tail, next_rel_loc)
        if tail == '': break        
            
    if found:
        return (last_sandbox, last_rel_loc)
    else:
        return (None, None)
    
def file2string(file):
    with open(file, 'r') as f:
        content=f.read()
    return content

def _get_root_env(file, enclosure):
    xmltext=file2string(file)
    xmldoc = minidom.parseString(xmltext)
    
    # TODO: this assumes only single entry of environ in XML.  
    env_root=xmldoc.getElementsByTagName(enclosure)[0] #self.__config.xmlenclosure)[0] 
            
    return env_root

def _get_available_env_files(path, envnodes,): #packageenv, personaleenv):
    ''' get environments files starting from path.
        adds list of import files and convert them to environment schema '''
    node_files=[]
    if path is not None:
        #sys_env_file = os.path.join(path,projectenv)
        #if  os.path.isfile(sys_env_file):
        #    node_files.project=sys_env_file
        
        for node in envnodes:
            env_file = os.path.join(path, node)
            if  os.path.isfile(env_file):
                node_files.append(env_file)
                envlogger.debug('envnode file: {}'.format(env_file))
        
    return node_files

def _mk_env_var(attrib): # logger):
    var=EnvVar(**attrib)
    if isinstance(var.export, str) :
        try:
            var.export=ast.literal_eval(var.export)
        except Exception:
            envlogger.critical('Wrong export flag value: {}; must be True of False.'.format(var.export))
            raise EnvironError('Bad value in export flag for {}; must be True of False'.format(var.name))
    if isinstance(var.override, str) :
        try:
            var.override=ast.literal_eval(var.override)
        except Exception:
            envlogger.critical('Wrong override flag value: {}; must be True of False.'.format(var.override))
            raise EnvironError('Bad value in override flag for {}; must be True of False'.format(var.name))
    return var

def _update_var(source_map, override, trace_env): #, logger):
    ''' Update surce_map with override env variable.
    Consider its override quality before doing so. '''
    name=override.name
    try: 
        current=source_map[name]
    except KeyError:
        source_map[name]=override
        if trace_env:
            if isinstance(trace_env, list):
                if name in trace_env or not trace_env:
                    envlogger.debug('\tEnvtrace: ({}):\n\tinitial: {} @ {}'\
                                 .format(name, override.value, override.origin))
    else:
        if current.override:
            override.origin=str(current.override) + ',' + override.origin
            source_map[name]=override
            if trace_env:
                if isinstance(trace_env, list):
                    if name in trace_env or not trace_env:
                        envlogger.debug('\tEnvtrace: ({}):\n\tcurrent: {} @ {}\n\toverride: {} @ {}'\
                                     .format(name, current.value, current.origin,
                                             override.value, override.origin))
        else:
            msg='Trying to override {}; source {}; offender {};'\
                .format(name, current.origin, override.origin)
            envlogger.critical(msg)
            raise EnvironError('Trying to override variable that is not set to allow override')

def _make_node_schema(node_files, enclosure, trace_env): #, logger):
    ''' Builds environment dictionary out of node_files.
    personal overrides package which overrides project environment.
    
    Args:
        node_files: list of env node files.
    '''
    env_map=OrderedDict()
    #files=filter(lambda f: f is not None, 
    #             [node_files.package, node_files.personal])
    files=node_files
    #[node_files.project, node_files.package, node_files.personal])
    for file in files:
        envlogger.debug('Loading schema: {}'.format(file))
        root=_get_root_env(file, enclosure=enclosure)
        for child in root.childNodes: 
            if child.nodeType != child.ELEMENT_NODE:
                continue
            tag=child.nodeName.lower()
            if child.attributes is None:
                print('No attributes: ', child.nodeName)
            attrib=OrderedDict(child.attributes.items()) 
            if tag == 'var':
                if 'value' not in attrib.keys():
                    value=None
                    if child.firstChild is not None:
                        value=child.firstChild.nodeValue
                    attrib['value'] = value 
                var=_mk_env_var(attrib,)
                if isinstance(var.export, str) :
                    var.export=ast.literal_eval(var.export)
                if isinstance(var.override, str) :
                    var.override=ast.literal_eval(var.override)
                
                var.origin=file
                _update_var(source_map=env_map, override=var, trace_env=trace_env, ) 
                    
                ''' rest will be set with unused attributes '''
                var.rest=OrderedDict(set(attrib.items())-set(var._asdict().items()))
            elif tag == 'import':
                var=EnvImport(**attrib)
                env_map[var.name]=var 
        root=None    
    return env_map
'''
    End definition of utilities
'''
        
class Environ(object):
    ''' Environ class is Accord way to manage environment variables.
        There are three level of environment files:
            .envpkg.xml is project level definitions and extension. 
            .envovr.xml is 'this' package overrides and extension. 
            <environment> clause in Part overrides and extension.
            
        ground rules when overriding environment variable:
            value can be override only if it is defined as such in parent environment 
            cast can be override although it consistency would be best practices.
            override quality can be only removed by derivative environment; 
            once removed, cannot be added back by derivative environments.
            '''
    
    def __init__(self, osenv=True, trace_env=None, logclass=None, logger=None):
        ''' Instantiates Environ object by setting its internal dictionary. 
        Args:
            osenv: if True, inherit os.environ
            
            configure: dict of name override to default setting:
               {'.packageenv':'.packageenv',
                '.personalenv':'.personalenv',
                'xmlenclosure':'environ'}
                
        Returns: Environ object filled according to tree environment settings.
        Access environ dictionary directly by its attribute environ.
        '''
        
        self.trace_env=trace_env
        self.logclass = None
        global envlogger
        if logclass:
            self.logclass = '.'.join([logclass, type(self).__name__])
            envlogger=logging.getLogger(self.logclass)
        elif logger:
            envlogger=logger.getChild(__name__)
                        
        if self.trace_env is not None:
            envlogger.setLevel(logging.DEBUG)
            if not envlogger.hasHandlers():
                handler=logging.StreamHandler(stream=sys.stdout)
                formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
                handler.setFormatter(formatter)            
                envlogger.addHandler(handler)
            
        self.__config=CONFIGURE
        
        self.envnodes=self.__config['envnodes']
        
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
            env: list of EnvVar records to use as overrides.
            path: node path to start with.  Defaults to Current Working Directory.
            envtree: if set will attempt to load environment tree from root location to path
                
        Returns: Environ object filled according to tree environment settings.
        Access environ dictionary directly by its attribute environ.
        '''
        
        stack=inspect.stack()
        caller=stack[1]
        if path:
            path=os.path.abspath(path)
        elif len(caller) > 1:
            caller_loc=os.path.dirname(caller[1])
            path=caller_loc
        
        if path is not None and envtree:
            if not os.path.exists(path):
                raise EnvironError('Path not found: {}'.format(path))
            self.path=path
            self.__build_env_tree(path=path)
        elif envtree:
            self.path=os.getcwd()
            self.__build_env_tree(path=self.path)
            
        if env is not None:
            #env_type=type(env)
            if isinstance(env, list):
                env_items=env
            elif isinstance(env, collections.Mapping):
                env_items=env.values()
            else:
                raise EnvironError('Unknown env type: {}'.format(type(env).__name__))
            for var in env_items:
                try:
                    self.environ[var.name]=var.value
                except Exception as e:
                    if not isinstance(var, EnvVar):
                        raise EnvironError('Only EnvVar are allowed in "env", but received {}'.format(type(var).__name__))
                    else:
                        raise EnvironError('Unknown error when assigning vars from env; {}'.repr(e))
                    
        return self
        
    def __getitem__(self, key):
        try:
            var=self.environ[key]
        except KeyError:
            raise
        return var.value
    
    ''' TODO: allow other type by adding cast according to its type '''
    def __setitem__(self, key, value):
        assert isinstance(value, EnvVar), 'Illegal value {} provided; must be EnvVar' 
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

    def __eval_env_schema_bottom_up(self, env_schema):
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
                
                if envvar.cast is not None and envvar.cast != 'string' and isinstance(envvar.value, str):
                    ''' TODO: check why sub fields cannot be variables '''
                    #vardict=var._asdict()
                    #envvar.rest=dict([(n,expandvars(source=v,environ=self)) \
                    #                  for n,v in vardict.items()])
                    
                    envvar.rest['value']=envvar.value
                    try:
                        envvar.value=cast_value(name=envvar.name, target_type=envvar.cast,
                                                attrib=envvar.rest,logclass=self.logclass)
                        envvar.rest=None
                    except KeyError:
                        msg='Unknown cast: {}; varname {}; origin: {}'\
                            .format(envvar.cast,envvar.name,envvar.origin)
                        raise EnvironError(msg)
                    else:
                        envvar.cast=envvar.cast
                        
                self.environ[envvar.name]=envvar   
                if envvar.export:
                    os.environ[envvar.name]=str(envvar.value)
                if self.trace_env:
                    if isinstance(self.trace_env, list):
                        if envvar.name in self.trace_env or not self.trace_env:
                            envlogger.debug('\tEnvtrace: eval ({}): {}'\
                                              .format(envvar.name, envvar.value))
       
            else:
                msg='Unknown var type: {}; needs to be EnvVar only'\
                    .format(var.cast, var.name, var.origin)
                raise EnvironError(msg)                          

    def __eval_env_schema_top_down(self):
        names=list(self.environ.keys())
        names.reverse()
        for name in names:
            envvar=self.environ[name]
            value=envvar.value
            if isinstance(value, str):
                new_value=expandvars(source=value,environ=self)  
                envvar.value=new_value
                if self.trace_env:
                    if value != new_value and isinstance(self.trace_env, list):
                        if envvar.name in self.trace_env or not self.trace_env:
                            envlogger.debug('\tEnvtrace: expand var ({}): from: {} to: {}'\
                                              .format(envvar.name, value, envvar.value))                          
            if envvar.export:
                os.environ[envvar.name]=str(envvar.value)
                if self.trace_env:
                    if isinstance(self.trace_env, list):
                        if envvar.name in self.trace_env or not self.trace_env:
                            envlogger.debug('\tEnvtrace: export var ({}): {}'\
                                              .format(envvar.name, envvar.value))                          
            # MYDEBUG:
            #if envvar.name == 'AC_LOG_CENTRAL':
            #    #trace=inspect.stack()
            #    print('AC_LOG_CENTRAL', envvar)
            #    traceback.print_stack()
            if envvar.cast is not None and envvar.cast != 'string' and isinstance(envvar.value, str):
                ''' TODO: check why sub fields cannot be variables '''
                vardict=envvar._asdict()
                #envvar.rest=dict([(n,expandvars(source=v,environ=self)) \
                #                  for n,v in vardict.items()])
                envvar.rest=vardict
                envvar.rest['value']=envvar.value
                value=envvar.value
                cast=envvar.cast
                try:
                    envvar.value=cast_value(name=envvar.name, target_type=envvar.cast,
                                            attrib=envvar.rest,logclass=self.logclass)
                    envvar.rest=None
                except KeyError:
                    msg='Unknown cast: {}; varname {}; origin: {}'\
                        .format(envvar.cast,envvar.name,envvar.origin)
                    raise EnvironError(msg)
                #else:
                #    envvar.cast=envvar.cast
            self.environ[envvar.name]=envvar   
            if self.trace_env:
                if isinstance(self.trace_env, list):
                    if envvar.name in self.trace_env or not self.trace_env:
                        envlogger.debug('\tEnvtrace: eval ({}/{}): from:  {} to: {}'\
                                          .format(envvar.name, envvar.cast, value, envvar.value))
                    
    def __build_env_tree(self, path):
        # Load environment vars as is from path into schema tree
        env_schema=self.__get_env_path(path)
        
        # first walk bottom up to evaluate vars - only expand vars.
        self.__eval_env_schema_bottom_up(env_schema)
        self.__eval_env_schema_top_down()
                
    def __get_env_node(self, path, config):
        ''' get environments files starting from path.
            adds list of import files and convert them to environment schema '''
        #node_files=_EnvNode()
        if path is not None:
            node_files=_get_available_env_files(path=path, #projectenv=self.DOTPROJECTENV, 
                                                #packageenv=self.PACKAGEENV, 
                                                #personaleenv=self.PERSONALENV
                                                envnodes=config['envnodes'],
                                                )
            envlogger.debug('Found node schema {}: \n\t{}'.format(path, repr(node_files)))
            node_env=_make_node_schema(node_files, enclosure=self.__config['enclosure'], trace_env=self.trace_env) #, logger=self.logger)
        return node_env
    
    
    def __update_env_map(self, source_map, override_map):
        ''' 
        Description:
            Update source_map with vars from override_map. 
            Take override quality into considerations 
        Args:
        Returns:
        Raises:
        
        '''
        if len(source_map) >0:
            for name, var in override_map.items():
                if isinstance(var, EnvVar):
                    _update_var(source_map=source_map, override=var, trace_env=self.trace_env) #, logger=logger) 
                elif isinstance(var, EnvImport):
                    source_map[name]=var
                else:
                    msg='Unknown var type: {}; needs to be EnvVar or EnvImport'\
                        .format(var.cast, var.name, var.origin)  
                    raise EnvironError(msg)                 
        else:
            source_map.update(override_map) 
    
    def __adopt_project_config( self, project_loc ):
        config=CONFIGURE
        config_file=os.path.join(project_loc, ENV_CONFIG_FILE)
        if os.path.isfile( config_file):
            root=_get_root_env(config_file, 'environ')
            envnodes_elms = root.getElementsByTagName('envnodes') 
            if ( envnodes_elms.length >1 ):
                raise EnvironError("Found {} envnodes tags bu only 1 allowed: {}",format(envnodes_elms.length(), ))
            envnodes_elm = envnodes_elms.item(0)
            
            if envnodes_elm:
                envnodes=envnodes_elm.firstChild.nodeValue
                if envnodes:
                    config['envnodes']=[x.strip() for x in envnodes.split(',')]
        return config
    
    def __get_nodes_on_path(self, path):
        ''' find nodes to evaluate by walking the tree and fetching 
                   environment files '''
        path=expandvars( path, environ=self )
        envlogger.debug('Evaluating file: {}'.format( path ))
        env_nodes=list()
        if not pathhasvars( path ):
            path=os.path.abspath( path )
            (project_loc, relative_loc)=advise_project_loc( path=path ) #, mark=mark)
            config=self.__adopt_project_config( project_loc )
            
            if relative_loc is not None:
                '''find nodes to evaluate by walking the tree and fetching 
                   environment files '''
                head=relative_loc
                rel_nodes=list()
                while head:
                    head, tail=os.path.split( head )
                    if tail:
                        rel_nodes.append( tail )               
                rel_nodes.reverse()
                
                start=project_loc
                nodes=[start]
                for node in rel_nodes:
                    if node:
                        start=os.path.join(start, node)
                        nodes.append(start)
                for node in nodes:
                    env_node=self.__get_env_node(path=node, config=config)
                    if len(env_node) > 0:
                        env_nodes.append(env_node) 
            else:
                raise EnvironError("Cannot find root project for: {}".format(path))
        return env_nodes
            
        
    def __get_env_path( self, path ):
        ''' Gets the environment schema representing Path.
        This include fetching all environment nodes from path to its project. 
        For each path node, we add its environment into list (env nodes).
         '''
        #mark=self.DOTPROJECTENV
        
        path=expandvars( path, environ=self )
        envlogger.debug('Evaluating file: {}'.format( path ))
        
        env_nodes=self.__get_nodes_on_path(path)
        
        ''' Combine all path nodes into single dict - override in order'''
        env_path_raw=OrderedDict()
        
        for env_node in env_nodes:
            self.__update_env_map(env_path_raw, env_node)
                
        ''' Now that that env nodes are consolidated - bring in imports. '''
        env_path=OrderedDict()
        for name, var in env_path_raw.items():
            if not isinstance(var, EnvImport):
                env_path[name]=var
            else: # this is import
                if var.path:
                    # by path - load from path
                    path=expandvars(var.path, env_path)
                    path=os.path.abspath(path)
                else:
                    # by name - find package location to import it environment
                    import importlib
                    package=importlib.import_module(var.name)
                    if package:
                        path=package.__path__
                        if isinstance(path, list):
                            path=path[0]
                    else:
                        msg='Cannot find {} to import; please make sure it is on PYTHONPATH or add path attribute'.format(path)
                        envlogger.critical(msg)
                        raise EnvironError(msg)
                envlogger.debug('Importing environment: {}'.format(path))
                if pathhasvars(path):
                    raise EnvironError('Trying to import named {} with unresolved path: {}'.format(name, path))
                env_import=self.__get_env_path(path)
                self.__update_env_map(env_path, env_import) 
                
        return env_path
        
    @classmethod
    def cmd_line_env(cls, env):
        ''' This function is deprecated, please use commandline instead '''
        return cls.commandline(env=env)
        
    @classmethod
    def commandline(cls, env):
        environ=Environ(osenv=False)
        if env is not None:
            for item in env:
                parts=item.split('=')
                name=parts[0]
                value='='.join(parts[1:])
                environ.environ[name]=EnvVar(name=name, value=value, 
                                             override=True, export=True)
                os.environ[name]=value
                    
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
            
    def update_env(self, *args, **kwargs):
        ''' This method is deprecated.  it is replaced by updates()'''
        return self.updates(*args, **kwargs) 
    
    def updates(self, input_environ, force_override=False, prefix_replace=None, prefix_add=None, prefix_exclusicve=True): 
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
        if input_environ is not None:
            env_type=type(input_environ)
            if env_type is list:
                input_items=input_environ
            elif env_type is OrderedDict or env_type is dict:
                input_items=input_environ.values()
            else:
                input_items=list()
            
            for var in input_items:
                input_var=self.__make_var(var, prefix_replace=None, prefix_add=None, prefix_exclusicve=True)
                try:
                    self_var=self.environ[input_var.name]
                except KeyError:
                    ''' if not found in existing Environ - just update Environ '''
                    if isinstance(input_var.value, str):
                        input_var.value=expandvars(input_var.value, self)
                    self.environ[input_var.name]=input_var
                    if self.trace_env:
                        if isinstance(self.trace_env, list):
                            if input_var.name in self.trace_env or not self.trace_env:
                                envlogger.debug('\tEnvtrace: ({}):\n\tnew by update function: {}'\
                                             .format(input_var.name, input_var.value,))
                else:
                    ''' if in Environ, override only if defined as such. '''
                    if self_var.override and not input_var.input or force_override:
                        if isinstance(input_var.value, str):
                            input_var.value=expandvars(input_var.value, self)
                        origin_var=self.environ[input_var.name]
                        self.environ[input_var.name]=input_var
                        if self.trace_env:
                            if isinstance(self.trace_env, list):
                                if input_var.name in self.trace_env or not self.trace_env:
                                    envlogger.debug('\tEnvtrace: ({}):\n\toverwrite by update function: {} @ {}'\
                                                 .format(input_var.name, input_var.value, origin_var.value))
                        
                ''' Export to process' Environ if defined as such '''
                if input_var.export:
                    value=input_var.value
                    if not isinstance(value, str):
                        value=str(value)
                    os.environ[input_var.name]=value
        return self

    def __copy__(self):
        env=Environ()
        for name, var in self.environ.items():
            v=var.__asdict()
            v['value']=copy(var.value)
            env[name]=EnvVar(**var._asdict()) #.value
        return env
            
    def __deepcopy__(self, memo):
        env=Environ()
        for name, var in self.environ.items():
            v=var._asdict()
            v['value']=deepcopy(var.value, memo)
            env[name]=EnvVar(**var._asdict()) #.value
        return env
    
    def _asdict(self):
        env=OrderedDict()
        for name, var in self.environ.items():
            env[name]=copy(var.value)
        return env
                
    def log_env(self, log=None):
        if log is None:
            log=lambda x: print(x)  
        msg=map(lambda x: '{k}={v} ({t})'.format(k=x, v=self.environ[x].value, 
                                                 t=type(self.environ[x].value).__name__), 
                sorted(self.environ.keys()))
        log('Environ Begin:\n\t'+'\n\t'.join(msg)+'\nEnviron End.')
        
    def __clean_env_var(self, var):
        default=DEFAULT_ENVVAR
        if isinstance(var, EnvVar):
            var=var._asdict()
        clean=list(filter(lambda x: x[1] != default[x[0]] and x[0] not in NONE_XML_FIELD, 
                          var.items()))
        return OrderedDict(clean)
        
    
    def __xml_repr(self, root=None):
        if root is not None:
            env=etree.SubElement(root, self.__config['enclosure'])
        else:
            env=etree.Element(self.__config['enclosure'])
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
    

