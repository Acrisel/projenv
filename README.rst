projenv provides mechanism for project to manage parameters for programs in
hierarchical way.

Overview
========
Environment is a special type of dictionary, holding parameters used by parts.
There are multiple levels and types of environments playing part in program
run. Environment evaluation process walks the project tree from top to program
location.  In each non-root node (package branch), there could be one file
defining nodes of environment. In root note there could be two types. In
addition ability  overwrite variables in personal setting is supported using
personalenv file.


Definitions
===========
+-------+------------+-----------------------------------------------------+
| Number| Name       | Description                                         |
+=======+============+=====================================================+
| 1     |.projectenv | read-only project level environment variables; also |
|       |            | identifies project root location.                   |
+-------+------------+-----------------------------------------------------+
| 2     | packageenv | addon environment for given read-only environment   |
|       |            | in local or upper environments.                     |
+-------+------------+-----------------------------------------------------+
| 3     | personalenv| personal overrides for project or package           |
|       |            | environment. It may include only overrides.         |
+-------+------------+-----------------------------------------------------+

Program Interface
=================

Within programs there are three types of access points to the environment variables.
To get projenv dictionary, program can perform the following command:

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

   Environ(self, osenv=True, configure=None, trace_env=None, logclass=None, logger=None)

+----------+------------------------------------------------------+------------------------------+
| Name     |Description                                           |Default Values                |
+==========+======================================================+==============================+
| osenv    | If set, load os environ.                             | True                         |
+----------+------------------------------------------------------+------------------------------+
| configure| Dictionary overriding default names for environment  | .projectenv : .projectenv    |
|          | files.                                               |  packageenv : packageenv     |
|          |                                                      |  personalenv : personalenv   |
|          |                                                      |  envtag : environ            |
+----------+------------------------------------------------------+------------------------------+
| trace_env| List of enviornment variables to trace               |  None                        |
+----------+------------------------------------------------------+------------------------------+
| logclass | If provided the string will be used for trace naming.|  None                        |
+----------+------------------------------------------------------+------------------------------+
| logger   | If set to True and logclass=None, use Python         |  None                        |
|          | getChild to set trace name.                          |                              |
+----------+------------------------------------------------------+------------------------------+


In addition to file name overrides, configuration dictionary can provide syntax used in these files and the environment root
tag under which environment variables are defined.


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

At each node, environment is evaluated in the following sequence:
   1. .projectenv, if available, is read and set.
   2. Next packageenv, if available, is read and set.
   3. Finally, personalenv overrides, if available, is read and set.

Example environment tree in a project.
Program A will include environment setting of Project and Package A locations.
Program AB will include Program A, Package A and Package AB accordingly.

     Project
         - .projectenv
         -  packageenv
         -  personalenv
         -  Program A
         -  Package A
              - packageenv
              - personalenv
              - Package AB
                    - packageenv
                    - personalenv
                    - Program AB


Example for project environment file
************************************

Core environment is tagged under <environ>.
Environ mechanism would look for this tag.  Once found, it would evaluate its content as environment directive.

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

Note: <environment> tag is to provide enclosure to environ.
Environ mechanism is not depending on its existent per se.  However, some kind on enclosure is required;  <environ> can not be in top level of the XML.


Example of Multiple Project Environment Tree
********************************************

At each import, environment is evaluated in the following sequence:
   1. First get the node representation of imported path.
   2. Evaluate it recursively (loading imports).
   3. Finally, insert the resulted imported map instead of the import directive (flat).


Project A: /Users/me/projs/proja/.projectenv.xml

.. code-block:: xml

  <environment>
    <environ>
      <var name='FILE_LOC' value='/Users/me/tmp/' export='True'/>
      <var name='FILE_NAME' value='aname' export='True'/>
      <var name='FILE_PATH' value='${FILE_LOC}${FILE_NAME}' export='True'/>
    </environ>
  </environment>


Project B: /Users/me/projs/projb/.projectenv.xml'

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

**Note**:import path can only include environment variables that are in the OS level pre-eveluation.



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
