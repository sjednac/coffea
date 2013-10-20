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
        node1.id = 'node1'
        node2.id = 'node2'
        node1.connections = ['node2']
         
        model = mock.MagicMock()
        model.nodes = [node1, node2]

        plotter = Plotter(model)
        graph = plotter.graph

        self.assertIsNotNone(graph)
        self.assertEqual(len(graph.nodes()), 2)
        self.assertEqual(len(graph.edges()), 1)

    def test_plotting(self):
        node1, node2 = mock.MagicMock(), mock.MagicMock()
        node1.id = 'node1'
        node2.id = 'node2'
        node1.connections = ['node2']
         
        model = mock.MagicMock()
        model.nodes = [node1, node2]

        plotter = Plotter(model)
        try:
            work_dir = tempfile.mkdtemp()
            filename = os.path.join(work_dir, 'test.png')
            
            self.assertFalse(os.path.exists(filename))
            plotter.plot(filename=filename)
            self.assertTrue(os.path.exists(filename))
        finally:
            shutil.rmtree(work_dir)
        
