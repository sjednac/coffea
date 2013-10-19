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

import mock
import tempfile
import unittest

from coffea.builder import Builder, PackageNodeFactory, ClassNodeFactory

class TestBuilder(unittest.TestCase):

    def test_append(self):
        with mock.patch('coffea.builder.JavaClass') as JavaClass:
            instance = JavaClass.return_value
            instance.package = 'com.example'
            instance.package_dependencies.return_value = ['com.example.service']
     
            builder = Builder()
            builder.model.merge = mock.MagicMock()

            with tempfile.NamedTemporaryFile(suffix='.class') as f:
                builder.append(f.name)
                self.assertTrue(builder.model.merge.called)
                #TODO: Check merge arguments
                
                
    def test_package_node_factory(self):
        java_class = mock.MagicMock()
        java_class.package = 'com.example'
        java_class.package_dependencies = mock.MagicMock(return_value=['com.example.service', 'com.example.model'])
        
        factory = PackageNodeFactory()
        node = factory.get_node(java_class)

        self.assertTrue(node)
        self.assertEqual(node.id, 'com.example')
        self.assertEqual(node.connections, set(['com.example.service', 'com.example.model']))
    
    def test_class_node_factory(self):
        java_class = mock.MagicMock()
        java_class.name = 'Test'
        java_class.class_dependencies = mock.MagicMock(return_value=['com.example.service.TestService', 'com.example.model.TestModel'])
       
        factory = ClassNodeFactory()
        node = factory.get_node(java_class)

        self.assertTrue(node)
        self.assertEqual(node.id, 'Test')
        self.assertEqual(node.connections, set(['com.example.service.TestService', 'com.example.model.TestModel']))
        
