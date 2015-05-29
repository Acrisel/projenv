'''
Created on Dec 29, 2013

@author: arnon
'''

import os.path
import xml.etree.ElementTree as xmltree
import xml.etree.ElementTree as etree
from collections import OrderedDict
import functools

#from namedlist import namedlist as Record
from namedlist import namedlist as Record
from .expandvars import expandvars
from .cast_value import cast_value

EnvVar=Record('EnvVar', [('name', None),
                         ('value', None),
                         ('override',True),
                         ('input', False),
                         ('cast', 'string'),
                         ('export', False),
                         ('encrypt', None),
                         ('rest', None)
                        ])

_EnvTrees=Record('_EnvTrees', [('project', None), 
                             ('package', None), 
                             ('personal', None)])

class EnvironError(Exception):
    def __init__(self, msg):
        self.msg=msg
        
    def __repr__(self):
        return "Environ error: "+repr(self.msg)
    
    def __str__(self):
        return "Environ error: "+repr(self.msg)
    
DOTPROJECTENV='.projectenv'
PROJECTENV='projectenv'
DOTPACKAGEENV='.packageenv'
PACKAGEENV='packageenv'
PERSONALENV='personalenv'
ENVTAG='envtag'

ENV_SYNTAX_EXT={'XML':'.xml',}

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
    
    if mark is None:
        mark=DOTPROJECTENV + ENV_SYNTAX_EXT['XML']
        
    cwd=os.getcwd() if path is None or path == '' else path
    #(sandbox, rel_loc)=os.path.split(cwd)
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
        
    def __init__(self, env=None, path=None, envtree=True, osenv=True, syntax='XML', config=None): 
        ''' Instantiates Environ object by setting its internal dictionary. 
        Args:
            env: lest of EnvVar records to use as overrides.
            path: node path to start with.  Defaults to Current Working Directory.
            envtree: if set will attempt to load environment tree from root location to path
            osenv: if True, inherit os.environ
            syntax: structure of environment files, default XML
            
            config: dict of name override to default setting:
               {'.projectenv':'.projectenv',
                'packageenv':'packageenv',
                'personalenv':'personalenv',
                'envtag':'environ'}
                
        Returns: Environ object filled according to tree environment settings.
        Access environ dictionary directly by its attribute environ.
        '''
        
        self.__config={DOTPROJECTENV:DOTPROJECTENV,
                       PACKAGEENV:PACKAGEENV,
                       PERSONALENV:PERSONALENV,
                       ENVTAG:'environ'}
        if config is not None:
            assert isinstance(config, dict), \
                    'Environ config argument must be of dict but found {}'.\
                    format(type(config).__name__)
                                
            self.__config.update(config)
        
        self.__syntax=syntax
        try:
            self.__ext=ENV_SYNTAX_EXT[syntax]
        except KeyError:
            assert True, 'Failed to find syntax extension, unsupported syntax {}.'.format(syntax)
        self.DOTPROJECTENV=self.__config[DOTPROJECTENV]+self.__ext
        self.PACKAGEENV=self.__config[PACKAGEENV]+self.__ext
        self.PERSONALENV=self.__config[PERSONALENV]+self.__ext
        
        self.environ=OrderedDict()
        if osenv:
            for name, value in os.environ.items():
                self.environ[name]=EnvVar(name=name, value=value)
        
        if path is not None and envtree:
            if not os.path.exists(path):
                raise EnvironError('Path not found: {}'.format(path))
            self.path=path
            self.env_trees=self.__get_env_tree(path=path)
            self.__load_env()
        elif envtree:
            self.path=os.getcwd()
            self.env_trees=self.__get_env_tree(path=self.path)
            self.__load_env()
            
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
        return self.environ.items()
    
    def values(self):
        return self.environ.values()
    
    def get(self, key):
        var=self.environ.get(key)
        if var is not None:
            value=var.value
        else:
            value=None
        return value
    
    def __get_root_env_map(self, root_tag):
        env_root=root_tag.find(self.__config[ENVTAG])
        root_map=self.__get_env_map(env_root)
        return root_map
                
    def __get_env_node(self, path):
        env_trees=_EnvTrees()
        if path is not None:
            sys_env_file = os.path.join(path,self.DOTPROJECTENV)
            if  os.path.isfile(sys_env_file):
                sys=sys_env_file
                tree=xmltree.parse(sys)
                root=tree.getroot()
                env_map=self.__get_root_env_map(root)
                env_trees.project=env_map
            else:
                env_trees.project={}
            prj_env_file = os.path.join(path, self.PACKAGEENV)
            if  os.path.isfile(prj_env_file):
                prj=prj_env_file
                tree=xmltree.parse(prj)
                root=tree.getroot()
                env_map=self.__get_root_env_map(root)
                env_trees.package=env_map
            else:
                env_trees.package={}
            lcl_env_file = os.path.join(path, self.PERSONALENV)
            if  os.path.isfile(lcl_env_file):
                lcl=lcl_env_file
                tree=xmltree.parse(lcl)
                root=tree.getroot()
                env_map=self.__get_root_env_map(root)
                env_trees.personal=env_map   
            else:
                env_trees.personal={}      
        return env_trees
    
    def __get_env_tree(self, path):
        mark=self.DOTPROJECTENV
        (project_loc, relative_loc) = advise_project_loc(path=path, mark=mark)
        if relative_loc is not None:
            rel_nodes=relative_loc.split('/')
            if project_loc == os.path.abspath(os.sep):
                raise EnvironError("Project environment file {} doesn't exist for: {}".format(self.DOTPROJECTENV,path))
            start=project_loc
            nodes=[start]
            for node in rel_nodes:
                start=os.path.join(start, node)
                nodes.append(start)
            env_nodes=list()
            for node in nodes:
                env_nodes.append(self.__get_env_node(path=node))  
            return env_nodes  
        else:
            raise EnvironError("Project environment file {} doesn't exist for: {}".format(self.DOTPROJECTENV,path))
            
    def __build_var_alter(self, var, alter):
        new_var=var
        if var.override \
          and alter is not None \
          and len(alter)>0:
            new_root=alter[0]
            new_alter=alter[1:]
            this_var=self.__build_var(var=var, prime=new_root
                         , alter=new_alter)
            if this_var is not None:
                new_var=this_var
        return new_var
    
    def __build_var(self, var, prime, alter):
        prime_var=prime.get(var.name)
        if prime_var is not None:
            if prime_var.override:
                new_var=self.__build_var_alter(prime_var, alter)
            else:
                new_var=prime_var
            del prime[prime_var.name]
        else:
            ''' not in prime - go down the line '''
            new_var=self.__build_var_alter(var, alter)
        return new_var
    
    @classmethod
    def __get_env_map(self, root):
        ''' Reads XML properties as environment starting from root '''
        env_map=OrderedDict()
        for child in root:
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
            
        return env_map
            
    def __build_environ(self, head, tail):
        ''' load head first, then continue with tail. 
            When loading var from head, check for overrides in tail.'''
        thisvars=list(head.values())
        for var in thisvars:
            built_var=self.__build_var(var=var, prime=head, alter=tail)
            built_var.value=expandvars(source=built_var.value, environ=self)
            
            if var.export:
                os.environ[var.name]=built_var.value
            
            if var.cast is not None:
                var.rest=dict([(n,expandvars(source=v, environ=self)) for n,v in var.rest.items()])
                var.rest['value']=built_var.value
                try:
                    built_var.value=cast_value(target_type=var.cast, attrib=var.rest)
                    built_var.rest=None
                except KeyError:
                    pass
                else:
                    built_var.cast=var.cast
            self.environ[var.name]=built_var


        ''' Run down the tail but skipp the last one: local.  
           This can only include overrides hence already loaded.'''
        if len(tail) >1:
            next_head=tail[0]
            next_tail=tail[1:]
            self.__build_environ(head=next_head, tail=next_tail)
            
    def __load_node_env(self, envnode):
        '''Updates environ with project variables from read from 
        .acmisc.props and acmisc.props '''        
        
        if envnode.project is not None and envnode.package is not None:
            project_env_root=envnode.project.find(self.__config[ENVTAG])
            project_map=self.get_env_map(project_env_root)
            package_env_root=envnode.package.find(self.__config[ENVTAG])
            package_map=self.get_env_map(package_env_root)
            personal_map={}
            if envnode.personal is not None:
                personal_env_root=envnode.personal.find(self.__config[ENVTAG])
                personal_map=self.get_env_map(personal_env_root)
            self.__build_environ(head=project_map, tail=[package_map, personal_map])
        return self
    
    def __load_env(self):
        '''Updates environ with project variables from read from 
        .acmisc.props and acmisc.props ''' 
        flat=functools.reduce(lambda x,y: x+[y.project, y.package, y.personal], self.env_trees, list())
        head=flat[0] if len(flat) > 0 else list()
        tail=flat[1:] if len(flat) > 1 else list()
        self.__build_environ(head=head, tail=tail)
        return self
    
    @classmethod
    def cmd_line_env(cls, env):
        environ=Environ(envtree=False, osenv=False)
        if env is not None:
            for item in env:
                parts=item.split('=')
                name=parts[0]
                value='='.join(parts[1:])
                environ.environ[name]=EnvVar(name=name, value=value)
        return environ
    
    def write(self, env_file=None):
        doc=etree.ElementTree()
        env=doc.Element('environment')
        for _, value in self.environ.items():
            env.SubElement(env, tag='var', attrib=value._asdict() )
        #doc_file=self.conf_file if env_file is None else env_file
        if env_file is not None:
            doc.write(env_file)
            
    def update_env(self, environ): #base_environ=None, overrides={}):
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
                try:
                    current_var=self.environ[var.name]
                except KeyError:
                    ''' if not found in existing Environ - just update Environ '''
                    if isinstance(var.value, str):
                        var.value=expandvars(var.value, self)
                    self.environ[var.name]=var
                else:
                    ''' if in Environ, override only if defined as such. '''
                    if current_var.override and not var.input:
                        if isinstance(var.value, str):
                            var.value=expandvars(var.value, self)
                        self.environ[var.name]=var
                        
                ''' Export to process' Environ if defined as such '''
                if var.export:
                    value=var.value
                    if not isinstance(value, str):
                        value=str(value)
                    os.environ[var.name]=value
        return self
            
    def dup_env(self):
        env={}
        for name, var in self.environ.items():
            env[name]=var.value
        return env
        
    def print_env(self, log=None):
        mylog=print if log is None else log
        msg=map(lambda x: '{k}={v}'.format(k=x, v=self.environ[x].value), 
                sorted(self.environ.keys()))
        mylog('Environ Begin:\n\t'+'\n\t'.join(msg)+'\n\tEnviron End.')
        
    def xml_repr(self, root=None):
        if root is not None:
            env=etree.SubElement(root, self.__config[ENVTAG])
        else:
            env=etree.Element(self.__config[ENVTAG])
            root=env
        for key in self.environ.keys():
            etree.SubElement(env, 'var', attrib={key:self.environ[key].value})
        return root

    def __repr__(self):
        txt='environ: {\n' #'Environ Begin:\n'
        body=[]
        for key in sorted(self.environ.keys()):
            body.append('\t({key}={value})'.format(key=key, value=self.environ[key].value))
        txt+='\n'.join(body)+'}\n' #'Environ End.\n'
        return txt
