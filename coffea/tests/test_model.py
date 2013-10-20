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
import unittest

from coffea.model import Model, Node, NodeIdFilter, NodeIdMapper

class TestModel(unittest.TestCase):

    def test_merge(self):
        model = Model()

        nodes = [Node('node0', ['node1']), 
                 Node('node1', ['external0']), 
                 Node('node2'),
                 Node('node0', ['node2'])]
        for n in nodes:
            model.merge(n)

        self.assertEquals(len(model.nodes), 3)
        self.assertEquals(model.nodes[0].id, 'node0')
        self.assertEquals(model.nodes[0].connections, set(['node1', 'node2']))
        self.assertEquals(model.nodes[1].id, 'node1')
        self.assertEquals(model.nodes[1].connections, set(['external0']))
        self.assertEquals(model.nodes[2].id, 'node2')
        self.assertEquals(model.nodes[2].connections, set([]))

    def test_standard_node_filters(self):
        model = Model()

        nodes = [Node('node0', ['node1']), 
                 Node('node1'), 
                 Node('node2'),
                 Node('node0', ['node2'])]
      
        model.node_filters.append(NodeIdFilter(lambda node_id: node_id is not 'node1'))
        model.node_filters.append(NodeIdMapper(lambda node_id: node_id.upper()))
        
        for n in nodes:
            model.merge(n)

        self.assertEquals(len(model.nodes), 2)
        self.assertEquals(model.nodes[0].id, 'NODE0')
        self.assertEquals(model.nodes[1].id, 'NODE2')
        self.assertEquals(model.nodes[0].connections, set(['NODE2']))
    
    def test_remove_external_connections(self):
        model = Model()
        nodes = [Node('node0', ['node1', 'node2', 'ext0']), 
                 Node('node1', ['ext1']), 
                 Node('node2'),
                 Node('node3', ['ext0', 'node2', 'ext1', 'ext2', 'ext3'])]

        for n in nodes:
            model.merge(n)

        self.assertEqual(model.remove_external_connections(), 6)
        
        self.assertEquals(len(model.nodes), 4)
        self.assertEquals(model.nodes[0].id, 'node0')
        self.assertEquals(model.nodes[0].connections, set(['node1', 'node2']))
        self.assertEquals(model.nodes[1].id, 'node1')
        self.assertEquals(model.nodes[1].connections, set([]))
        self.assertEquals(model.nodes[2].id, 'node2')
        self.assertEquals(model.nodes[2].connections, set([]))
        self.assertEquals(model.nodes[3].id, 'node3')
        self.assertEquals(model.nodes[3].connections, set(['node2']))
    
        self.assertRaises(AssertionError, model.merge, nodes[0])

    def test_node_repr(self):
        node = Node('sample')
        self.assertEquals(str(node), 'sample')

