import os
import sys

from distutils.sysconfig import get_python_lib
from setuptools.dist import Distribution
from setuptools import find_packages

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

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False
    
setup_info = {
    'name':package_name,
    'version':version,
    'url':'http://www.acrisel.com/accord/',
    'author':'Django Software Foundation',
    'author_email':'foundation@djangoproject.com',
    'description':('A high-level Python Web framework that encourages '
                 'rapid development and clean, pragmatic design.'),
    'license':'BSD',
    'include_package_data':True,
    'distclass':BinaryDistribution,
    #'packages':packages,
    'packages':find_packages(exclude=[]),
    'package_data':package_data,
    #'scripts':['accord/bin/accord-admin.py'],
    #'py_modules':['pem'],
    'include_package_data':True,
    'classifiers':[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Framework :: IDLE',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.6',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        #'Topic :: Internet :: WWW/HTTP',
        #'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        #'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
}

if __name__ == '__main__':
    import pprint
    pprint.pprint(setup_info)