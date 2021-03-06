import os
import sys

from setuptools import setup
from distutils.sysconfig import get_python_lib

''' 
is the Python package in your project. It's the top-level folder containing the 
__init__.py module that should be in the same directory as your setup.py file
/-
  |- README.rst
  |- CHANGES.txt
  |- setup.py
  |- dogs 
     |- __init__.py
     |- catcher.py

To create package and upload:

  python setup.py sdist
  python setup.py sdist upload

'''
PACKAGE = "projenv" 

'''
NAME is usually similar to or the same as your PACKAGE name but can be whatever you want. 
The NAME is what people will refer to your software as, the name under which your 
software is listed in PyPI and—more importantly—under which users will install it 
(for example, pip install NAME).
'''
NAME = PACKAGE

'''
DESCRIPTION is just a short description of your project. A sentence will suffice.
'''
DESCRIPTION = '''ProjEnv allows the use of hierarchical parameter structure for projects.'''

'''
AUTHOR and AUTHOR_EMAIL are what they sound like: your name and email address. This 
information is optional, but it's good practice to supply an email address if people 
want to reach you about the project.
'''
AUTHOR = 'Acrisel Team'
AUTHOR_EMAIL = 'support@acrisel.com'

'''
URL is the URL for the project. This URL may be a project website, the Github repository, 
or whatever URL you want. Again, this information is optional.
'''
URL = 'https://github.com/Acrisel/projenv'
version_file=os.path.join(PACKAGE, 'VERSION.py')
with open(version_file, 'r') as vf:
    vline=vf.read()
VERSION = vline.strip().partition('=')[2].replace("'", "")

scripts=['projenv/export_projenv.py',
         'projenv/export_projenv.sh',
         'projenv/mkprojenvpackage.py',
         'projenv/mkprojenvoverride.py',
         'projenv/mkprojenvdirs.py',
         'projenv/projenv_template_envpackage.xml',
         'projenv/projenv_template_envoverride.xml',
         'projenv/addprojenv2virtualenv.py', ]

other_files=['projenv/projenv_template_envpackage.xml',
             'projenv/projenv_template_envoverride.xml',]

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Accord are
# still present in site-packages. See #18115.
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
        
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, 'projenv'))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break

setup_info={'name': NAME,
 'version': VERSION,
 'url': URL,
 'author': AUTHOR,
 'author_email': AUTHOR_EMAIL,
 'description': DESCRIPTION,
 'long_description': open("README.rst", "r").read(),
 'license': 'MIT',
 'keywords': 'project, sandbox, virtualenv, virtualenvwrapper, configuration, parameters',
 'packages': [PACKAGE],
 'scripts' : scripts,
 'package_data':{'': other_files},
 'include_package_data':True,
 'install_requires': ['python-dateutil>=2.4.2',
                      'namedlist>=1.7',],
 'extras_require': {'dev': [], 'test': []},
 'classifiers': ['Development Status :: 5 - Production/Stable',
                 'Environment :: Other Environment',
                 #'Framework :: Project Settings and Operation',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Topic :: Software Development :: Libraries :: Application '
                 'Frameworks',
                 'Topic :: Software Development :: Libraries :: Python '
                 'Modules']}
setup(**setup_info)


if overlay_warning:
    sys.stderr.write("""

========
WARNING!
========

You have just installed ProjEnv over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Accord. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install ProjEnv.

""" % {"existing_path": existing_path})
