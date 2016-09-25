from setuptools import setup, find_packages

setup(name='uc-chalk-rip',
    version = '0.1',
    description = "Ripper for Uchicago's chalk site",
    author="Reid McIlroy-Young",
    author_email = "reidmcy@uchicago.edu",
    license = 'GPL',
    packages = find_packages(),
    entry_points={'console_scripts': [
              'chalk_rip = chalk_rip:main',
              ]},
)
