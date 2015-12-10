from setuptools import setup

setup(name='uvcclient',
      version='0.3',
      description='A remote control client for Ubiquiti\'s UVC NVR',
      author='Dan Smith',
      author_email='dsmith+uvcclient@danplanet.com',
      url='http://github.org/kk7ds/uvcclient',
      packages=['uvcclient'],
      scripts=['uvc'],
      install_requires=[],
      tests_require=['mock'],
)
