try:
    from setuptools import setup, find_namespace_packages
except ImportError:
    from distutils.core import setup

setup(
    name='vsurt',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy >= 1.6.2',
    ],
    packages=[
        'vsurt.dashboard',
        'vsurt.urdk',
        'vsurt.urmsgs',
        'vsurt'
    ],
)
