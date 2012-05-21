from setuptools import setup
setup(
      name='SlideGen',
      version='0.0.0.1 pre',
      packages=['slidegen'],
      author='reyoung',
      author_email='reyoung@126.com',
      license='LGPL',
      install_requires=["PyYAML>=3.10","Markdown>=2.1.1","tornado>=2.2"],
      entry_points ={
        'console_scripts':[
            'SlideGen=slidegen.SlideGen:Main'
        ]
      },
      keywords ='html5 slide generator',
      url='https://github.com/reyoung/SlideGen'
)