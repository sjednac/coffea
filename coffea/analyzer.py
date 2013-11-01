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
import matplotlib as mlt
import matplotlib.pyplot as plt
import networkx as nx
import os

log = logging.getLogger('analyzer')

class Analyzer(object):
    """Abstract base class for model analyzers."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, model):
        """Initializes a new instance of the Analyzer class."""
        
        self.model = model
        self._graph = None

    @property
    def graph(self):
        """Returns a NetworkX graph model.""" 

        if self._graph is None:
            self._graph = self._build_graph(self.model)
        return self._graph

    def _build_graph(self, model):
        log.debug('Building NetworkX graph...')
        graph = nx.DiGraph()
        for node in model.nodes:
            graph.add_node(node.id, size=node.size)
    
        for node in model.nodes:
            for conn in node.connections:
                graph.add_edge(node.id, conn) 

        log.debug('NetworkX graph size: nodes=%d edges=%d', graph.number_of_nodes(), graph.number_of_edges())        
        return graph


class Writer(Analyzer):
    """A graph model writer"""
    
    def __init__(self, model):
        """Initializes a new instance of the Writer class."""
        super(Writer, self).__init__(model)
    
    def write(self, path, data_format='dot'):
        """Writes the underlying graph model to a specific file."""
        
        if data_format == 'dot':
            nx.write_dot(self.graph, path)
        elif data_format == 'gml':
            nx.write_gml(self.graph, path)
        elif data_format == 'graphml':
            nx.write_graphml(self.graph, path)
        else:
            raise AssertionError('Invalid format: %s' % data_format)


class Plotter(Analyzer):
    """A graph plotter."""

    node_colors = ['#ffd070', '#e6ff6f', '#ff886f', '#6f9eff', '#cf6fff']

    def __init__(self, model):
        """Initializes a new instance of the Plotter class."""
        super(Plotter, self).__init__(model)

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
   
        if 'calc_node_size' in kwargs and kwargs['calc_node_size']:
            node_size = self._node_size_vector
            if node_size is None:
                node_size = 300
        else:  
            node_size = 300 
            
        log.debug('Drawing nodes...') 
        nx.draw_networkx_nodes(self.graph, positions, 
                               node_color=self.node_colors, 
                               node_size=node_size,
                               alpha=0.8)
        
        log.debug('Drawing edges...') 
        nx.draw_networkx_edges(self.graph, positions, 
                               edge_color='#666666', 
                               alpha=0.75)
        
        log.debug('Drawing labels...') 
        nx.draw_networkx_labels(self.graph,positions, 
                                font_color='#222222', 
                                font_family='courier new',
                                font_weight='bold')
        
        log.debug('Plotting graph...')
        try: 
            filename = kwargs['filename']
            plt.savefig(filename, bbox_inches='tight')
        except KeyError:
            plt.show()

    @property
    def _node_size_vector(self):
        log.debug('Calculating size vector...')
        size_vect = []
        for _, attrs in self.graph.nodes_iter(data = True):
            if 'size' in attrs:
                size_vect.append(attrs['size'])
            else:
                # External node may not have a size attribute
                size_vect.append(0)

        max_val = max(size_vect)
        if max_val != 0:
            log.debug('Normalizing size vector...')
            size_vect = [200 + s / (max_val*1.0)*800 for s in size_vect]
        else:
            size_vect = None       

        return size_vect
    
