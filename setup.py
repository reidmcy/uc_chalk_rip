from setuptools import setup, find_packages

version = '0.1'

setup(name='uc-chalk-rip',
    version = version,
    description = "Ripper for Uchicago's chalk site",
    author="Reid McIlroy-Young",
    author_email = "reidmcy@uchicago.edu",
    license = 'GPL',
    url="https://github.com/reidmcy/uc_chalk_rip",
    download_url = "https://github.com/reidmcy/uc_chalk_rip/archive/{}.tar.gz".format(version),
    packages = find_packages(),
    entry_points={'console_scripts': [
              'chalk_rip = chalk_rip:main',
              ]},
)
