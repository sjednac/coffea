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

import logging
import os
import sys

from java.java_class import JavaClass
from java.java_scanner import JavaScanner 

from model import Model, Node

log = logging.getLogger('builder')

class Builder(object):
    """Dependency model builder."""
    
    def __init__(self):
        """Initializes a new instance of the Builder class."""
        self.model = Model()
    
    def append(self, root_path):
        """Appends artifacts from the specified path to the underlying model."""
        
        log.info('Scanning path: %s', root_path)
        classes = 0
        with JavaScanner() as scanner:
            scanner._process_class = self._process_class 
            classes = scanner.scan(root_path)
            
        log.info('Scan finished. Found %d class files.', classes)

    #TODO: NodeCreator with 2 default implementations (PackageNodeCreator and ClassNodeCreator) 
    def _process_class(self, path):
        node = self._create_node(JavaClass(path))
        log.debug('Processing node: %s', node)
        self.model.merge(node)
    
    def _create_node(self, java_class):
        return Node(java_class.package, java_class.package_dependencies())

