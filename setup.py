from setuptools import setup, find_packages

version = '2025.04.1'

setup(
    name='toolshed',
    version=version,
    description='Tools for managing data backups',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
    ],
    keywords='backups pruning data archives MySQL Plone Python',
    author='Paul Rentschler',
    author_email='paulrentschler@gmail.com',
    url='https://github.com/paulrentschler/toolshed',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
)
