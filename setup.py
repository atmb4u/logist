from setuptools import setup
from logist import __version__

setup(name='logist',
      version=__version__,
      description="Easy logging system for humans and machines",
      url='https://github.com/atmb4u/logist',
      author='Anoop Thomas Mathew',
      author_email='atmb4u@gmail.com',
      license='BSD',
      packages=['logist'],
      zip_safe=False, requires=['redis'],
      install_requires=[
          "redis"
      ]
      )
