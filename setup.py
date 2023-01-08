from setuptools import setup, Extension

name = 'MagmaBook'
version = "0.0.0"
install_requires = [
    'bottle',
]
package_dir = {'': 'src',
               'MagmaBook': 'src/backend/MagmaBook',
               'frontend': 'src/frontend'}
packages = ['MagmaBook', 'frontend']

# C extension
ext_modules = [
    Extension('MagmaBookCApi', sources=['src/extensions/Api.c',
                                        'src/extensions/MagmaBook.c',
                                        'src/extensions/ComputedPayloads.c',
                                        'src/extensions/RawPayloads.c',
                                        ],
              include_dirs=['include', 'src/extensions'])]

# Run setup:
kwargs = {"name": name,
          "version": version,
          "install_requires": install_requires,
          "ext_modules": ext_modules,
          "packages": packages,
          "package_dir": package_dir,
          "include_package_data": True,
          }
setup(**kwargs)
