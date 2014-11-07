#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Szymon Biliński 
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

glassfish_home = os.getenv('GLASSFISH_HOME', '/opt/glassfish')

output_format='dot'
output_file='output/glassfish_dependencies.dot'

### Logger ###
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('scanner').setLevel(logging.WARN)
logging.getLogger('java').setLevel(logging.WARN)


### Analysys ###
from coffea.builder import Builder, PackageNodeFactory
from coffea.analyzer import Writer 
from coffea.model import NodeIdFilter, NodeIdMapper

# Build a package dependency model using code size as weight
b = Builder(PackageNodeFactory(size_property="code"))

# Drop packages that don't belong to the org.glassfish namespace
b.model.node_filters.append(NodeIdFilter(lambda it: it.startswith('org.glassfish.')))

# Drop the org.glassfish prefix for clarity
b.model.node_filters.append(NodeIdMapper(lambda it: it.replace('org.glassfish.', '')))

# Reduce all child packages to the top level package (eg. "ejb.xyz" and "ejb.abc.pqr" will be merged into "ejb")
b.model.node_filters.append(NodeIdMapper(lambda it: it.split('.')[0]))

# Remove unimportant packages
#b.model.node_filters.append(NodeIdFilter(lambda it: it not in ['logging']))

# Run the analysis 
b.append(glassfish_home)

print 'Nodes: ', len(b.model.nodes)

### Export data ###
writer = Writer(b.model)
writer.write(output_file, data_format=output_format)

