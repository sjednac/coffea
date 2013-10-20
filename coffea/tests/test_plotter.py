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
import mock
import os
import shutil
import tempfile
import unittest

from coffea.plotter import Plotter

class TestPlotter(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_graph_builder(self):
        node1, node2 = mock.MagicMock(), mock.MagicMock()
        node1.id, node1.size, node1.connections = 'node1', 42, set(['node2', 'external1'])
        node2.id, node2.size, node2.connections = 'node2', 0, set([])
         
        model = mock.MagicMock()
        model.nodes = [node1, node2]

        plotter = Plotter(model)
        graph = plotter.graph

        self.assertIsNotNone(graph)
        self.assertEqual(len(graph.nodes()), 3)
        self.assertEqual(len(graph.edges()), 2)
        
        for n, d in graph.nodes_iter(data = True):
            if n == 'node1':
                self.assertTrue('size' in d)
                self.assertEqual(d['size'], 42)
            elif n == 'node2':
                self.assertTrue('size' in d)
                self.assertEqual(d['size'], 0)
            elif n == 'external1':
                self.assertFalse('size' in d)
            else:
                self.fail('Unexpected node: %s' % n)

    def test_plotting(self):
        node1, node2 = mock.MagicMock(), mock.MagicMock()
        node1.id, node1.size, node1.connections = 'node1', 100, set(['node2', 'external1'])
        node2.id, node2.size, node2.connections = 'node2', 0, set([])
         
        model = mock.MagicMock()
        model.nodes = [node1, node2]

        try:
            work_dir = tempfile.mkdtemp()
           
            with mock.patch('coffea.plotter.Plotter._node_size_vector') as nsv_mock:
                nsv_mock.__get__ = mock.MagicMock()

                plotter = Plotter(model)

                filename = os.path.join(work_dir, 'test1.png')
            
                self.assertFalse(os.path.exists(filename))
                plotter.plot(filename=filename)
                self.assertTrue(os.path.exists(filename))
                self.assertFalse(nsv_mock.__get__.called) 

            with mock.patch('coffea.plotter.Plotter._node_size_vector') as nsv_mock:
                nsv_mock.__get__ = mock.MagicMock(return_value=[1000, 200, 200])

                plotter = Plotter(model)

                filename = os.path.join(work_dir, 'test2.png')
            
                self.assertFalse(os.path.exists(filename))
                plotter.plot(filename=filename, calc_node_size=True)
                self.assertTrue(os.path.exists(filename))
                self.assertTrue(nsv_mock.__get__.called) 
        
        finally:
            shutil.rmtree(work_dir)
       
    def test_node_size_vector(self):
        node1, node2 = mock.MagicMock(), mock.MagicMock()
        node1.id, node1.size, node1.connections = 'node1', 0, set(['node2', 'external1']) 
        node2.id, node2.size, node2.connections = 'node2', 0, set([])

        model = mock.MagicMock()
        model.nodes = [node1, node2]
        
        plotter1 = Plotter(model)
        self.assertIsNone(plotter1._node_size_vector)

        node1.size = 100
        
        plotter2 = Plotter(model)
        self.assertListEqual(plotter2._node_size_vector, [1000, 200, 200])


