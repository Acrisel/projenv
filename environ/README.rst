=======
PROJENV
=======

Overview
========

projenv provides mechanism for project to manage parameters for programs in
hierarchical way.
Environment is a special type of dictionary holding parameters used by parts. 
There are multiple levels and types of environment files playing part in program run.


Environment node
================

Environment evaluation process walks the project tree from top to program location. 
In each node it looks for set of files that defines the environment parameters.
By default, environment is derived from two type of files as each node:

+-------+------------------+------------------------------------------------+
| Number| Name             | Description                                    |
+=======+==================+================================================+
| 1     | .envpackage.xml  | environment parameters for the package.        |
+-------+------------------+------------------------------------------------+
| 2     | .envoverride.xml | personal overrides for package environment. It |
|       |                  | may include re-define parameters with override |
|       |                  | ride=True.                                     |
+-------+------------------+------------------------------------------------+

Project can alter this default behavior by defining **.envconfig.xml** at its root 
with specific value for envnodes.

.. code-block:: xml

  <environ>
    <envnodes>.envproject, .envpackage, .envoverride</envnodes>
  </environ>
  
Environment node must also have __init__.py.  Each folder in the project hierarchy must have __init__.py file; this is since the search for parent folder stops when a folder is found not to have __init__.py file.

**Important**: without __init__.py in the packages that have .envpackage.xml and .envoverride.xml, Environ will fail to load.

Program Interface
=================

Within programs there are three types of access points to the 
environment variables. To get projenv dictionary, program can 
perform the following command:

1. Loading environment variables from project structure 
2. Updating environment variable in program
3. Accessing environment variables

Loading environment variables
=============================

.. code-block:: python
   
   import projenv 
   env=projenv.Environ()

When Program evaluates environment, it starts with root location going down the tree up to and including package environment of Program location.

Environ class __init__ has the following signature

::

   Environ(self, osenv=True, trace_env=None, logclass=None, logger=None)

+----------+------------------------------------------------------+------------------------------+
| Name     |Description                                           |Default Values                |
+==========+======================================================+==============================+
| osenv    | If set, load os environ.                             | True                         |
+----------+------------------------------------------------------+------------------------------+
| trace_env| List of environment variables to trace               |  None                        |
+----------+------------------------------------------------------+------------------------------+
| logclass | If provided the string will be used for trace naming.|  None                        |
+----------+------------------------------------------------------+------------------------------+
| logger   | If set to True and logclass=None, use Python         |  None                        |
|          | getChild to set trace name.                          |                              |
+----------+------------------------------------------------------+------------------------------+

Within derivative articles environment can be updated with environment variable as follows.

Updating environment variables
==============================

.. code-block:: python

  env.updates([
    EnvVar(name='REJ_ALLOWED',cast='integer',value=0,input=True),
    EnvVar(name='OUT_FILE',value='${VAR_LOC}/summary.csv',cast='path', input=True),
    EnvVar(name='RATE',override='True',cast='integer',value=5,input=True)])


**If input is set to True** the variable update will be ignored if the variable is defined in parent environment. If variable is not defined in parent environment, it will be defined and set to value from the command.
**If input is set to False** update will overwrite variable value if variable exists, if variable is not defined it will define it.
**Override** flags environment variable as changeable by derivative program articles.


Accessing environment variables
===============================

.. code-block:: python

   import projenv
   env=projenv.Environ()
   env.updates([
   EnvVar(name='REJ_ALLOWED',cast='integer',value=0,input=True),
   EnvVar(name='OUT_FILE',value='${VAR_LOC}/summary.csv',cast='path', input=True),
   EnvVar(name='RATE',override='True',cast='integer',value=5,input=True)])

   ofile=env['OUT_FILE']
   rate=env.get('RATE')


In the first case(ofile variable), direct access, KeyError exception may be sent if variable name does not exist.
In the second example(rate variable), None value will be returned if not found.


Environment Tree
================

Environment files are evaluated in hierarchical way.  The project tree and its packages are treated as nodes in a tree.
Each node can be evaluated and have its own representation of the environment.

Single Project Environment Tree
*******************************

At each node, environment is evaluated in the sequence or envnodes configuration parameter. 
By default this means:

   1. First .envpackage.xml, if available, is read and set.
   2. Next, .envoverride.xml overrides, if available, is read and set.
   
As shown below, this behavior could be changed to support different 
environment node structure. For example, to support legacy projects using older 
version of projenv, the following configuration .envconfig.xml can be used:

.. code-block:: xml

  <environ>
    <envnodes>.projectenv, packageenv, personalenv</envnodes>
  </environ>

The following figure shows a possible use of default configuration.The structure below 
shows example environment tree in a project.  When the above command is engaged in 
Program A, it would include environment setting of Project and Package A locations. 
Program AB will include Program A, Package A and Package AB accordingly.

     Project
         -  envpackage
         -  envoverride
         -  Program A
         -  Package A
              - evpackage
              - envoverride
              - Package AB
                    - envpackage
                    - envoverride
                    - Program AB


The structure below shows example of an environment file. Core environment is tagged under 
< environ>. Environ mechanism would look for this tag. Once found, it would evaluate its 
content as environ- ment directive.

.. code-block:: xml

  <environment>
    <environ>
      <var name='AC_WS_LOC' value='${HOME}/sand/myproject' export='True'/>
      <var name='AC_ENV_NAME' value='test' export='True'/>
      <var name='AC_VAR_BASE' value='${HOME}/var/data/' export='True'/>
      <var name='AC_LOG_LEVEL' value='DEBUG' export='True'/>
      <var name='AC_LOG_STDOUT' value='True' override='True' export='True' cast='boolean'/>
      <var name='AC_LOG_STDOUT_LEVEL' value='INFO' override='True' export='True'/>
      <var name='AC_LOG_STDERR' value='True' override='True' export='True' cast='boolean'/>
      <var name='AC_LOG_STDERR_LEVEL' value='CRITICAL' override='True' export='True'/>
    </environ>
  </environment>

Note: <environment> tag is to provide enclosure to environ. Environ mechanism is not 
depending on its existent per se.  However, some kind on enclosure is required;  <environ> 
can not be in top level of the XML.


Example of Multiple Project Environment Tree
********************************************

At each import, environment is evaluated in the following sequence:
   1. First get the node representation of imported path.
   2. Evaluate it recursively (loading imports).
   3. Finally, insert the resulted imported map instead of the import directive (flat).


Project A: /Users/me/projs/proja/.envpackage.xml

.. code-block:: xml

  <environment>
    <environ>
      <var name='FILE_LOC' value='/Users/me/tmp/' export='True'/>
      <var name='FILE_NAME' value='aname' export='True'/>
      <var name='FILE_PATH' value='${FILE_LOC}${FILE_NAME}' export='True'/>
    </environ>
  </environment>


Project B: /Users/me/projs/projb/.envpackage.xml'

.. code-block:: xml

  <environment>
    <environ>
      <import name='proja' path='/Users/me/projs/proja/.projectenv.xml'/>
      <var name='FILE_NAME' value='bname' export='True'/>
    </environ>
  </environment>


The example above shows import project directive within project B's environment.  In project B's context, FILE_PATH variable will result with
the value /Users/me/tmp/bname.

**Recursive** inclusion of environments (recursive import statement) would cause evaluation of environment variables to be loaded recursively.
Consideration is given to overrides in post import environments.

**Note**: import must be set as full path for the installation of the included project. It is therefore best practice to populate real path 
only in .envoverride.xml and not in .envpackage.xml.

Best Practices
==============

So many options, so what should one do?

Naming Parameters
*****************

*Prefix* your parameters with an identifier. Specifically if your projects would 
need to cooperate (import their environment). We have all parameters us ’AC ’ as prefix. We 
also define ’AC PROJ PREFIX’ that can be used in program to construct parameter name.

We recommend following UNIX convention for environment variables. Use upper-case letters 
separated with underscore. We use this style in all of this document listings.

*Drivers and Derivatives*, for the sake of this discussion we define three types of parameters:
1. standalone is a parameter that is not dependent on another and is not used by another parameter.
2. driver is a parameter that other parameters defined by it.
3. derivative is a parameter that includes a driver in its definitions.

A parameter can be both a driver and derivative.
Use drivers and derivative parameter definition in such a way that users may personalize the 
behavior of the system. For example, developers may want to change their own directory structure to 
fit their own tools.

.envproject
***********

Dot (.) envproject, although not default in envnodes configuration, good practice to use. It 
is usually contains parameters that are good for the all projects. You can look at is as your 
standard parameters to all projects that you produce. In the following listing locations are 
defined as derivatives of AC VAR BASE. This is useful since users of this project can override 
that parameter to change to their own structure.

.. code-block:: xml

  <environment>
    <environ>
      <var name=’AC_PROJ_PREFIX’ value=’AC_’ export=’True’ override=’True’/>
      <var name=’AC_VAR_BASE’ value=’/var/accord/data/’ override=’True’ export=’True’/>
      <var name=’AC_ENV_NAME’ value=’.’ override=’True’ export=’True’/>
      <var name=’AC_VAR_LOC’ value=’${AC_VAR_BASE}${AC_ENV_NAME}/’ override=’True’ export=’True’/>
      <var name=’AC_LOG_LOC’ value=’${AC_VAR_LOC}/log/’ override=’True’ export=’True’/>
      <var name=’AC_REJ_LOC’ value=’${AC_VAR_LOC}/rej/’ override=’True’ export=’True’/>
      <var name=’AC_RUN_LOC’ value=’${AC_VAR_LOC}/run/’ override=’True’ export=’True’/>
      <var name=’AC_IN_LOC’ value=’${AC_VAR_LOC}/in/’ override=’True’ export=’True’/>
      <var name=’AC_OUT_LOC’ value=’${AC_VAR_LOC}/out/’ override=’True’ export=’True’/>
    </environ>
  </environment>

.envpackage
***********
Dot envpackage includes definitions for that are specific to the project or the package. 
Usually this is kept for things like RPC PORT or maybe MAIL SEND SMTP.

.envoverride
************

Dot envoverride provides means to personalize an environment. Users can override .envpackage default parameters settings. 

It is recommended to exclude envoverride from your code repository 
(e.g., add envoverride.xml to .gitignore). Otherwise, users may override each other 
personalizations.

Utilities
=========

**projenv** contains a few utilities to help initialize and use project or package environments.

mkprojenvpackage.py
*******************

**mkprojenvpackage.py** predominately creates .envpackage.xml parameter set.  It also creates .envoverride.xml parameter set unless instructed otherwise. 

Finally, it creates project folders as defined in the parameter set, if choose to do so.

Example
~~~~~~~

In this example , only var folder is being override (line 7)

.. code-block:: python
    :number-lines:

    $ mkdir teste
    $ cd teste
    $ touch __init__.py
    $ mkprojenvpackage.py 
    Enter project name (name of folder that will be created for project) [teste]: 
    Enter project version []: 
    Enter location for project's var folder [/var/data/teste]: /var/acrisel/data/teste
    Var space location /var/acrisel/data/teste don't exist, create? [Yes]: 
    Enter project prefix [TESTE_]: 
    Enter environment name [.]: 
    Successfully created projectenv /Users/tester/teste/.envpackage.xml
    Successfully created projectenv /Users/tester/teste/.envoverride.xml
    create project folders? [Yes]: 
    Creating project folders:
        TESTE_PROJ_LOC: Already exists /Users/tester/teste/
        TESTE_PROJ_API_LOC: Created /Users/tester/teste/api/
        TESTE_PROJ_DB_LOC: Created /Users/tester/teste/db/
        TESTE_PROJ_SRC_LOC: Created /Users/tester/teste/src/
        TESTE_PROJ_FMT_LOC: Created /Users/tester/teste/fmt/
        TESTE_PROJ_RES_LOC: Created /Users/tester/teste/res/
        TESTE_PROJ_CFG_LOC: Created /Users/tester/teste/cfg/
        TESTE_PROJ_DATA_LOC: Created /Users/tester/teste/data/
        TESTE_VAR_LOC: Created /var/acrisel/data/teste/./
        TESTE_LOG_LOC: Created /var/acrisel/data/teste/./log/
        TESTE_REJ_LOC: Created /var/acrisel/data/teste/./rej/
        TESTE_RUN_LOC: Created /var/acrisel/data/teste/./run/
        TESTE_IN_LOC: Created /var/acrisel/data/teste/./in/
        TESTE_OUT_LOC: Created /var/acrisel/data/teste/./out/
        TESTE_DB_LOC: Created /var/acrisel/data/teste/./db/
        TESTE_LKUP_LOC: Created /var/acrisel/data/teste/./lkup/
        TESTE_TMP_LOC: Created /var/acrisel/data/teste/./tmp/

Command line options
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    $ mkprojenvpackage.py -h
    usage: mkprojenvpackage.py [-h] [-t PATH] [-p PATH] [-n NAME] [-d PATH]
                               [-w PATH] [-x NAME] [-e NAME] [-v VERSION]
                               [--no-override] [--force-defaults]

    optional arguments:
      -h, --help            show this help message and exit
      -t PATH, --templates PATH
                            location of templates. defaults to projenv built-in
                            templates
      -p PATH, --project PATH
                            path to project. defaults to current working directory
      -n NAME, --name NAME  name to project. default for directory name of project
                            location
      -d PATH, --data PATH  location of data space where data projects are
                            created, default /var/data/(name of PROJECT)
      -w PATH, --work PATH  location of work space where processing in-work data
                            is created, default DATA space
      -x NAME, --prefix NAME
                            project prefix used for environment parameters names.
                            defaults to project name.
      -e NAME, --environment NAME
                            name to be use to personalize var area. Recommended to
                            use when multiple users use the same var area
      -v VERSION, --version VERSION
                            version for this project environment. Use if need to
                            bind environment version to project.
      --no-override         skips creation of .envoverride.xml
      --force-defaults      forces the use of default. this option skips
                            interaction


mkprojenvoverride.py
********************

Example 
~~~~~~~

In this example, tester only had .envpackage.xml file in project directory.  In building overrides, tester profides environment name (line 2).  as a result, var area is personalized with tester name (as oppose to previous example line 10)

.. code-block:: python
    :number-lines:

    $ mkprojenvoverride.py
    Enter environment name [.]: tester
    create project folders? [Yes]: 
    Creating project folders:
        TESTE_OUT_LOC: Created /var/acrisel/data/teste/tester/out/
        TESTE_LKUP_LOC: Created /var/acrisel/data/teste/tester/lkup/
        TESTE_PROJ_CFG_LOC: Created /Users/tester/teste/cfg/
        TESTE_TMP_LOC: Created /var/acrisel/data/teste/tester/tmp/
        TESTE_DB_LOC: Created /var/acrisel/data/teste/tester/db/
        TESTE_PROJ_SRC_LOC: Created /Users/tester/teste/src/
        TESTE_PROJ_DATA_LOC: Created /Users/tester/teste/data/
        TESTE_PROJ_RES_LOC: Created /Users/tester/teste/res/
        TESTE_PROJ_FMT_LOC: Created /Users/tester/teste/fmt/
        TESTE_REJ_LOC: Created /var/acrisel/data/teste/tester/rej/
        TESTE_LOG_LOC: Created /var/acrisel/data/teste/tester/log/
        TESTE_PROJ_LOC: Already exists /Users/tester/teste/
        TESTE_VAR_LOC: Already exists /var/acrisel/data/teste/tester/
        TESTE_PROJ_API_LOC: Created /Users/tester/teste/api/
        TESTE_RUN_LOC: Created /var/acrisel/data/teste/tester/run/
        TESTE_IN_LOC: Created /var/acrisel/data/teste/tester/in/
        TESTE_PROJ_DB_LOC: Created /Users/tester/teste/db/
        
Command line options
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    $ mkprojenvoverride.py -h
    usage: mkprojenvoverride.py [-h] [-t PATH] [-p PATH] [-e NAME]
                                [--force-defaults]

    optional arguments:
      -h, --help            show this help message and exit
      -t PATH, --templates PATH
                            location of templates. defaults to projenv built-in
                            templates
      -p PATH, --project PATH
                            path to project. defaults to current working directory
      -e NAME, --environment NAME
                            name to be use to personalize var area. Recommended to
                            use when multiple users use the same var area
      --force-defaults      forces the use of default. this option skips
                            interaction


mkprojenvdirs.py
****************

Creates project folders according 

Example
~~~~~~~

.. code-block:: python
    :number-lines:
    
    $ mkprojenvdirs.py
    create project folders? [Yes]: 
    Creating project folders:
        TESTE_PROJ_LOC: Already exists /Users/tester/teste/
        TESTE_PROJ_API_LOC: Created /Users/tester/teste/api/
        TESTE_PROJ_DB_LOC: Created /Users/tester/teste/db/
        TESTE_PROJ_SRC_LOC: Created /Users/tester/teste/src/
        TESTE_PROJ_FMT_LOC: Created /Users/tester/teste/fmt/
        TESTE_PROJ_RES_LOC: Created /Users/tester/teste/res/
        TESTE_PROJ_CFG_LOC: Created /Users/tester/teste/cfg/
        TESTE_PROJ_DATA_LOC: Created /Users/tester/teste/data/
        TESTE_VAR_LOC: Already exists /var/acrisel/data/teste/tester/
        TESTE_LOG_LOC: Already exists /var/acrisel/data/teste/tester/log/
        TESTE_REJ_LOC: Already exists /var/acrisel/data/teste/tester/rej/
        TESTE_RUN_LOC: Already exists /var/acrisel/data/teste/tester/run/
        TESTE_IN_LOC: Already exists /var/acrisel/data/teste/tester/in/
        TESTE_OUT_LOC: Already exists /var/acrisel/data/teste/tester/out/
        TESTE_DB_LOC: Already exists /var/acrisel/data/teste/tester/db/
        TESTE_LKUP_LOC: Already exists /var/acrisel/data/teste/tester/lkup/
        TESTE_TMP_LOC: Already exists /var/acrisel/data/teste/tester/tmp/
        
Command line options
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    $ mkprojenvdirs.py -h
    usage: mkprojenvdirs.py [-h] [-p PATH]

    optional arguments:
      -h, --help            show this help message and exit
      -p PATH, --project PATH
                            path to project. defaults to current working directory

export_projev.py and .sh
************************

**export_projenv.py** provide a function and command line access to get projects' environment parameters in appropriate shell format.
it sh partner, **export_projenv.sh** can be source to export environment parameters in current shell.  **source export_projenv.sh [project]**.

**export_projenv.sh** uses **export_projev.py** to produce exportable construct for UNIX shell.

Example
~~~~~~~

.. code-block:: python

    $ export_projenv.py --exclude-os
    export PROJENV_PREFIX="TESTE_"
    export TESTE_PROJ_NAME="teste"
    export TESTE_PROJ_VER=""
    export TESTE_PROJ_LOC="/Users/tester/teste/"
    export TESTE_PROJ_API_LOC="/Users/tester/teste/api/"
    export TESTE_PROJ_DB_LOC="/Users/tester/teste/db/"
    export TESTE_PROJ_SRC_LOC="/Users/tester/teste/src/"
    export TESTE_PROJ_FMT_LOC="/Users/tester/teste/fmt/"
    export TESTE_PROJ_RES_LOC="/Users/tester/teste/res/"
    export TESTE_PROJ_CFG_LOC="/Users/tester/teste/cfg/"
    export TESTE_PROJ_DATA_LOC="/Users/tester/teste/data/"
    export TESTE_ENCODING="ascii"
    export TESTE_BYTEORDER="network"
    export TESTE_ENV_NAME="tester"
    export TESTE_VAR_LOC="/var/acrisel/data/teste/tester/"
    export TESTE_LOG_LOC="/var/acrisel/data/teste/tester/log/"
    export TESTE_REJ_LOC="/var/acrisel/data/teste/tester/rej/"
    export TESTE_RUN_LOC="/var/acrisel/data/teste/tester/run/"
    export TESTE_IN_LOC="/var/acrisel/data/teste/tester/in/"
    export TESTE_OUT_LOC="/var/acrisel/data/teste/tester/out/"
    export TESTE_DB_LOC="/var/acrisel/data/teste/tester/db/"
    export TESTE_LKUP_LOC="/var/acrisel/data/teste/tester/lkup/"
    export TESTE_TMP_LOC="/var/acrisel/data/teste/tester/tmp/"
    export TESTE_LOG_LEVEL="DEBUG"
    export TESTE_LOG_STDOUT="False"
    export TESTE_LOG_STDOUT_LEVEL="INFO"
    export TESTE_LOG_STDERR="True"
    export TESTE_LOG_STDERR_LEVEL="WARNING" 
    
Command line options
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    $ export_projenv.py -h
    usage: export_projenv.py [-h] [-p PATH] [--shell {sh,ksh,bash}] [--exclude-os]

    optional arguments:
      -h, --help            show this help message and exit
      -p PATH, --project PATH
                            path to project. defaults to current working directory
      --shell {sh,ksh,bash}
                            bind the shell to be compatible with
      --exclude-os          does not add OS environ


Hook to Virtualenv and virtualenvwrapper
========================================

It is highly recommended to use virtualenv and virtualenvwrapper in conjunction to projenv.

To make this convenient, projenv has a hook into virtualenv: **addproj2virtualenv [path]>**.

Multiple projects mat be using the same virtualenv.  Once project is added to virtualenv, to get access to project features, **setproj <name>** should be used.

Once project is selected by **setproj**, **cdsand <tag>** can be used where tag is navigate to project sandbox base location parameter.  Similarly, **cdvar <tag>** can be used to navigate to var base location parameters.

Example
*******

Here we assume projenv templates were used to create a project.  Hence the following environment variables are used.  If project name is example, the following environment parameter will be part of the environment:

EXAMPLE_PROJ_LOC
EXAMPLE_PROJ_API_LOC
EXAMPLE_VAR_LOC
EXAMPLE_LOG_LOC

after **setproj example**, we can use the following navigational commands:

**cdproj**: will relocate to EXAMPLE_PROJ_LOC
**cdproj api** will relocate to EXAMPLE_PROJ_API_LOC
**cdvar** will relocate to EXAMPLE_VAR_LOC
**cdvar log** will relocate to EXAMPLE_LOG_LOC


Installation, validation and example program
============================================

How to install, validate installation and use the package?

Installation
************

To install run following command: pip install projenv

Validation
**********

test.py in github link below perform unit test cases to check projenv.

Example
*******

See example of the program using projenv on 
Github https://github.com/Acrisel/projenv/blob/master/environ/example/example

Backwards compatibility
=======================

Due the changes in naming of node base files, projects using previous version can do one of the following steps.

1. Change node files name to fit the new naming convention.
2. Add **.envconfig.xml** with proper envnodes definition as follows:

.. code-block:: xml

    <environ>
      <envnodes>.projectenv.xml, packageenv.xml, personalenv.xml</envnodes>
    </environ>
    
Also, each folder in the project hierarchy need to have __init__.py file; See environment node section above for more details.
 
Additional resources
====================

Documentation is in the "docs" directory and online at the design and use of projenv.

**example** and **tests** directory shows ways to use projenv.Environ . Both directories are available to view and download as part of source code
on GitHub. GitHub_link_

.. _GitHub_link: https://github.com/Acrisel/projenv

Docs are updated rigorously. If you find any problems in the docs, or think they
should be clarified in any way, please take 30 seconds to fill out a ticket in
github or send us email at support@acrisel.com

To get more help or to provide suggestions you can send as email to:
arnon@acrisel.com uri@acrisel.com
