#p!/usr/bin/env python
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

import os
import unittest

from coffea.java.java_class import JavaClass 
from coffea.java.tests import __file__ as test_directory

data_dir = os.path.join(os.path.dirname(test_directory), 'data')

class TestJavaClass(unittest.TestCase):

    def setUp(self):
        self.obj = JavaClass(data_dir+os.sep+'SimplePOJO.class')

    def test_declaration(self):
        self.assertEqual(self.obj.name, 'SimplePOJO')
        self.assertEqual(self.obj.package, '')
        self.assertEquals(self.obj.super_name, 'java.lang.Object')
        self.assertEquals(self.obj.interfaces, ['java.io.Serializable'])
        
        self.assertTrue(self.obj.public)
        self.assertTrue(self.obj.final)
        self.assertFalse(self.obj.abstract)
        self.assertFalse(self.obj.annotation)
        self.assertFalse(self.obj.enum)

    def test_fields(self):
        self.assertTrue(self.obj.fields)
        self.assertTrue(self._find_by_name(self.obj.fields, 'id'))
        self.assertTrue(self._find_by_name(self.obj.fields, 'name'))
        self.assertTrue(self._find_by_name(self.obj.fields, 'age'))
        self.assertTrue(self._find_by_name(self.obj.fields, 'cash'))
        self.assertTrue(self._find_by_name(self.obj.fields, 'matrix'))
        self.assertTrue(self._find_by_name(self.obj.fields, 'times'))

    def test_methods(self):
        self.assertTrue(self.obj.methods)
        self.assertTrue(self._find_by_name(self.obj.methods, 'doStuff'))
        self.assertTrue(self._find_by_name(self.obj.methods, 'toString'))

    def test_attributes(self):
        self.assertTrue(self.obj.attributes)
        self.assertTrue(self._find_by_name(self.obj.attributes, 'SourceFile'))

    def _find_by_name(self, seq, name):
        return filter(lambda it: it.name == name, seq) 

    def test_class_dependencies(self):
        self.assertEquals(self.obj.class_dependencies(), ['SimplePOJO', 
                                                          'java.io.Serializable', 
                                                          'java.lang.Double', 
                                                          'java.lang.Integer', 
                                                          'java.lang.Long', 
                                                          'java.lang.Object', 
                                                          'java.math.BigDecimal', 
                                                          'java.util.Date'])
    
    def test_package_dependencies(self):
        self.assertEquals(self.obj.package_dependencies(), ['', 
                                                            'java.io', 
                                                            'java.lang', 
                                                            'java.math', 
                                                            'java.util'])

