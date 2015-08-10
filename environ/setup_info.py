import os
import sys

from distutils.sysconfig import get_python_lib
from setuptools.dist import Distribution
from setuptools import find_packages
from collections import OrderedDict

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# define packages left out from packing/installing
# Example:
# EXCLUDE_FROM_PACKAGES = ['accord.conf.project_template',
#                          'accord.conf.app_template',
#                          'accord.bin']
#
EXCLUDE_FROM_PACKAGES = []

def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
package_name = 'projenv'

for dirpath, dirnames, filenames in os.walk(package_name):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_path = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_path):
        packages.append(package_path)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])

# Dynamically calculate the version based on accord.VERSION.
version_file = open(os.path.join(root_dir, 'VERSION'))
version = version_file.read().strip()

with open(os.path.join(root_dir, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()
    
import subprocess
subprocess.check_call('pip freeze > requirements.txt', shell=True)

with open(os.path.join(root_dir, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read() 
requirements=[ r for r in requirements.split('\n') if r]

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False
    
setup_info = OrderedDict([
    ('name', package_name),
    ('version',version),
    ('url','https://github.com/Acrisel/projenv'),
    ('author','Acrisel Team'),
    ('author_email','support@acrisel.com'),
    ('description','ProjEnv allows the use of hierarchical parameter structure for projects.'),
    ('long_description',long_description),
    ('license','MIT'),
    ('include_package_data',True),
    #('distclass',BinaryDistribution),
    ('keywords','project, virtualenv, parameters',),
    ('packages',find_packages(exclude=['example', 'example.*', 'tests', 'tests.*'])),
    ('install_requires', requirements),
    ('extras_require',{'dev': [],
                       'test': [],}),
    ('package_data',package_data),
    #'scripts':['accord/bin/accord-admin.py'],
    #'py_modules':['pem'],
    ('include_package_data',True),
    ('classifiers',[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Framework :: Project Settings and Operation',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]),
])

if __name__ == '__main__':
    import pprint
    import json
    pprint.pprint(setup_info)
    with open('setup_info.pkg', 'w') as f:
        json.dump(setup_info, f)