from distutils.core import setup

setup(name='ionexpert',
      version='1.0.0',
      license='MIT',
      packages=['ionexpert'],
      author='Tzoiker',
      author_email='tzoiker@gmail.com',
      python_requires='>=3.0.0',
      install_requires=[
          'pyserial'
      ],
      zip_safe=False)
