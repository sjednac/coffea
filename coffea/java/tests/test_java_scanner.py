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
import os
import shutil
import tempfile
import unittest
import zipfile

from coffea.java.java_scanner import JavaScanner

class Archive(object):

    def __init__(self, name='archive'):
        self.name = name
        self.files = []

    def __enter__(self):
        self._tmpdir = tempfile.mkdtemp()
        self.root_path = os.path.join(self._tmpdir, self.name)

        os.makedirs(self.root_path)

        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self._tmpdir)

    def __repr__(self):
        return 'Sample Archive:\n%s' % '\n'.join(self.files)

    def mkdir(self, root, name):
        path = os.path.join(root, name)
        os.makedirs(path)
        return path

    def mkfile(self, root, name):
        path = os.path.join(root, name)
        open(path, 'a').close()  
        self.files.append(path) 
    
    def mkzip(self, root, name, entries):
        path = os.path.join(root, name)
        zf = zipfile.ZipFile(path, "w")
        with tempfile.NamedTemporaryFile() as f:
            for e in entries:
                zf.write(f.name, e)
        zf.close()
        self.files.append(path)
        return path              
                                             
    def compress(self):
        path = os.path.join(self._tmpdir, 'compressed-'+self.name)
        zf = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)                                             
        for f in self.files:
            zf.write(f, f.replace(self.root_path, ''))
        zf.close()    
        return path                                                                                             


class SampleJar(Archive):

    def __init__(self):
        Archive.__init__(self, 'sample-lib.jar')

    def __enter__(self):
        Archive.__enter__(self)
        
        self.com_path = self.mkdir(self.root_path, 'com')
        self.com_example_path = self.mkdir(self.com_path, 'example')
       
        self.mkfile(self.com_example_path, 'Component.class')
        self.mkfile(self.com_example_path, 'ComponentImpl.class')
        
        return self
    
    def __repr__(self):
        return 'Sample Jar:\n%s\n%s\n%s' % ('*'*20, '\n'.join(self.files), '*'*20)


class SampleWar(Archive):
  
    def __init__(self):
        Archive.__init__(self, 'sample-webapp.war')
    
    def __enter__(self):
        Archive.__enter__(self)

        self.webinf_path = self.mkdir(self.root_path, 'WEB-INF')
        self.classes_path = self.mkdir(self.webinf_path, 'classes')
        self.lib_path = self.mkdir(self.webinf_path, 'lib')
        self.css_path = self.mkdir(self.root_path, 'css')
        self.img_path = self.mkdir(self.root_path, 'img')
  
        self.mkfile(self.webinf_path, 'web.xml') 
        self.mkfile(self.webinf_path, 'applicationContext.xml') 
       
        self.mkfile(self.classes_path, 'Controller.class') 
        self.mkfile(self.classes_path, 'Model.class') 
        self.mkfile(self.classes_path, 'View.class') 
  
        self.mkfile(self.root_path, 'index.jsp') 
        self.mkfile(self.css_path, 'main.css') 
        self.mkfile(self.img_path, 'logo.png') 
        
        self.mkzip(self.lib_path, 'service.jar', ['com/example/ServiceImpl.class', 'com/example/ServiceImplHelper.class'])
        self.mkzip(self.lib_path, 'service-api.jar', ['com/example/Service.class'])
        
        return self      

    def __repr__(self):
        return 'Sample War:\n%s\n%s\n%s' % ('*'*20, '\n'.join(self.files), '*'*20)
    

class SampleEar(Archive):
  
    def __init__(self):
        Archive.__init__(self, 'sample-app.ear')
    
    def __enter__(self):
        Archive.__enter__(self)

        self.metainf_path = self.mkdir(self.root_path, 'META-INF')
        self.lib_path = self.mkdir(self.root_path, 'lib')

        self.mkfile(self.metainf_path, 'application.xml') 
        self.mkfile(self.metainf_path, 'MANIFEST.MF') 
       
        self.mkzip(self.lib_path, 'commons.jar', ['com/example/CommonClass.class', 
                                                  'com/example/CommonClassFactory.class',
                                                  'com/example/CommonClassHelper.class'])
        
        self.mkzip(self.root_path, 'business-component.jar', ['com/example/Service.class', 
                                                              'com/example/ServiceBean.class'])
        
        #TODO: Create sample JARs in /WEB-INF/lib
        self.mkzip(self.root_path, 'sample-webapp.war', ['/WEB-INF/web.xml',
                                                         'com/example/CommonClass.class', 
                                                         'com/example/CommonClassHelper.class'])
        
        return self      

    def __repr__(self):
        return 'Sample Ear:\n%s\n%s\n%s' % ('*'*20, '\n'.join(self.files), '*'*20)
 


class TestJavaScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = JavaScanner(callback=mock.MagicMock())
        self.assertTrue(os.path.isdir(self.scanner._work_dir))

    def tearDown(self):
        self.scanner.dispose()
        self.assertFalse(os.path.isdir(self.scanner._work_dir))

    def test_supported_files(self):
        scanner = self.scanner
        def supported(name):
            with tempfile.NamedTemporaryFile(suffix=name) as f:       
                return scanner.supported_file(f.name)

        self.assertTrue(supported('Test.class'))
        self.assertTrue(supported('test-1.0.jar'))
        self.assertTrue(supported('test-1.0.war'))
        self.assertTrue(supported('test-1.0.ear'))
       
        self.assertFalse(supported('build.properties')) 
        self.assertFalse(supported('pom.xml')) 
        self.assertFalse(supported('build.gradle')) 
        self.assertFalse(supported('README')) 
        self.assertFalse(supported('Test.java')) 
      
    def test_scan_file(self):
        scanner = self.scanner
         
        with tempfile.NamedTemporaryFile(suffix = '.xml') as not_supported_file:
            scanner.callback.reset_mock()
            self.assertEquals(scanner.scan(not_supported_file.name), 0) 
            self.assertEquals(scanner.callback.call_count, 0)
         
        with tempfile.NamedTemporaryFile(suffix = '.class') as class_file:
            self.assertEquals(scanner.scan(class_file.name), 1) 
            self.assertEquals(scanner.callback.call_count, 1)
            scanner.callback.assert_any_call(class_file.name)

        with SampleJar() as exploded_jar:
            jar = exploded_jar.compress()
            scanner.callback.reset_mock()
            self.assertEquals(scanner.scan(jar), 2)
            self.assertEquals(scanner.callback.call_count, 2)
        
        with SampleWar() as exploded_war:
            war = exploded_war.compress()
            scanner.callback.reset_mock()
            self.assertEquals(scanner.scan(war), 6)
            self.assertEquals(scanner.callback.call_count, 6)
        
        with SampleEar() as exploded_ear:
            ear = exploded_ear.compress()
            scanner.callback.reset_mock()
            self.assertEquals(scanner.scan(ear), 7)
            self.assertEquals(scanner.callback.call_count, 7)
    
    def test_scan_directory(self):
        scanner = self.scanner

        with SampleJar() as exploded_jar:
            scanner.callback.reset_mock()
            self.assertEquals(scanner.scan(exploded_jar.root_path), 2)
            self.assertEquals(scanner.callback.call_count, 2)
        
        with SampleWar() as exploded_war:
            scanner.callback.reset_mock()
            self.assertEquals(scanner.scan(exploded_war.root_path), 6)
            self.assertEquals(scanner.callback.call_count, 6)

        with SampleEar() as exploded_ear:
            scanner.callback.reset_mock()
            self.assertEquals(scanner.scan(exploded_ear.root_path), 7)
            self.assertEquals(scanner.callback.call_count, 7)
    
    def test_with_contract(self):
        with JavaScanner(callback=mock.MagicMock()) as s:
            self.assertTrue(s)
            self.assertTrue(os.path.isdir(s._work_dir))
        self.assertFalse(os.path.isdir(s._work_dir))
