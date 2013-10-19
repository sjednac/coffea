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

import abc
import logging
import os
import sys

from java.java_class import JavaClass
from java.java_scanner import JavaScanner 

from model import Model, Node

log = logging.getLogger('builder')

class Builder(object):
    """Dependency model builder."""
    
    def __init__(self, node_factory=None):
        """Initializes a new instance of the Builder class."""
        self.model = Model()
        self.node_factory = node_factory if node_factory is not None else ClassNodeFactory()
    
    def append(self, root_path):
        """Appends artifacts from the specified path to the underlying model."""
        
        log.info('Scanning path: %s', root_path)

        classes = 0
        with JavaScanner(self._process_class) as scanner:
            classes = scanner.scan(root_path)
            
        log.info('Scan finished. Found %d class files.', classes)

    def _process_class(self, path):
        node = self.node_factory.get_node(JavaClass(path))
        log.debug('Processing node: %s', node)
        self.model.merge(node)
    

class NodeFactory(object):
    """Node factory."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_node(self, java_class):
        """Converts a JavaClass instance to a Node instance."""
        pass

class PackageNodeFactory(NodeFactory):
    """A NodeFactory for package dependency analysys."""

    def get_node(self, java_class):
        return Node(java_class.package, java_class.package_dependencies())

class ClassNodeFactory(NodeFactory):
    """A NodeFactory for class dependency analysys."""
    
    def get_node(self, java_class):
        return Node(java_class.name, java_class.class_dependencies())

