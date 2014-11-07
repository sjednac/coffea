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

### Config ###
import os

jboss7_home = os.getenv('JBOSS7_HOME', '/opt/jboss-7.2.0.GA')
jboss7_mods = jboss7_home +  "/modules"


### Logger ###
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('scanner').setLevel(logging.WARN)
logging.getLogger('java').setLevel(logging.WARN)


### Analysys ###
from coffea.builder import Builder, PackageNodeFactory
from coffea.analyzer import Plotter
from coffea.model import NodeIdFilter, NodeIdMapper

# Build a package dependency model using code size as weight
b = Builder(PackageNodeFactory(size_property="code"))

# Drop packages that don't belong to the org.jboss namespace
b.model.node_filters.append(NodeIdFilter(lambda it: it.startswith('org.jboss.')))

# Drop the org.jboss prefix for clarity
b.model.node_filters.append(NodeIdMapper(lambda it: it.replace('org.jboss.', '')))

# Reduce all child packages to the top level package (eg. "as.xyz" and "as.abc.pqr" will be merged into "as")
b.model.node_filters.append(NodeIdMapper(lambda it: it.split('.')[0]))

# Remove unimportant packages
b.model.node_filters.append(NodeIdFilter(lambda it: it not in ['logging']))

# Run the analysis 
b.append(jboss7_mods)

print 'Nodes: ', len(b.model.nodes)

p = Plotter(b.model)

# Plot using matplotlib
p.plot(calc_node_size=True)

# Plot to a file
#p.plot(filename='/tmp/jboss7_module_dependencies.png')

