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
import matplotlib as mlt
import matplotlib.pyplot as plt
import networkx as nx

log = logging.getLogger('plotter')

class Plotter(object):
    """A graph plotter."""

    node_colors = ['#ffd070', '#e6ff6f', '#ff886f', '#6f9eff', '#cf6fff']

    def __init__(self, model):
        """Initializes a new instance of the Plotter class."""
        
        self.model = model
        self._graph = None

    @property
    def graph(self):
        """Returns a NetworkX graph model.""" 

        if self._graph is None:
            self._graph = self._build_graph(self.model)
        return self._graph

    def plot(self, **kwargs):
        """Plots the underlying graph."""

        plt.figure(facecolor='#fefefe', dpi=80, frameon=True) 
        plt.axis('off')
        
        try:
            positions = nx.graphviz_layout(self.graph)
        except ImportError as err:
            log.info('Graphviz not available: error=%s', err)
            log.info('Falling back to spring layout...')
            positions = nx.spring_layout(self.graph)
        #FIXME: Caused by bin/coffea in some cases
        except TypeError as err:
            log.warn('Graphviz layout failed: error=%s', err)
            log.warn('Falling back to spring layout...')
            positions = nx.spring_layout(self.graph)

        nx.draw_networkx_nodes(self.graph, positions, 
                               node_color=self.node_colors, 
                               alpha=0.8)
        nx.draw_networkx_edges(self.graph, positions, 
                               edge_color='#666666', 
                               alpha=0.75)
        nx.draw_networkx_labels(self.graph,positions, 
                                font_color='#222222', 
                                font_family='courier new',
                                font_weight='bold')
        try: 
            filename = kwargs['filename']
            plt.savefig(filename, bbox_inches='tight')
        except KeyError:
            plt.show()
         
    def _build_graph(self, model):
        graph = nx.DiGraph()
        for node in model.nodes:
            graph.add_node(node.id)
    
        for node in model.nodes:
            for conn in node.connections:
                graph.add_edge(node.id, conn) 
        
        return graph


