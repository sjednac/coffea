#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2013 Szymon Biliński 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from distutils.core import setup

setup(
    name='coffea',
    version='0.1.0',
    license='Apache 2.0',
    author='Szymon Biliński',
    author_email='szymon.bilinski@gmail.com',
    packages=['coffea', 
              'coffea.java'],
    scripts=['bin/coffea'],
    description='Coffea: Java Dependency Graph Generator',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Topic :: Utilities'],
    keywords=('java', 
              'bytecode', 
              'dependency', 
              'scanner',
              'graph', 
              'generator')
)
