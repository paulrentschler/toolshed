from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='toolshed',
    version=version,
    description="Tools for managing data backups",
    classifiers=[
        "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
    ],
    keywords='backups pruning data archives MySQL Python',
    author='Paul Rentschler',
    author_email='paul@rentschler.ws',
    url='https://github.com/paulrentschler/toolshed',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
)
