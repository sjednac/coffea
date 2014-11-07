******
Coffea
******

Coffea is a command line tool and Python library for analyzing **static dependences** in **Java** bytecode. Features:

* Class processing handled entirely in Python (i.e. no JVM dependency and no class loader issues) 
* Recursive processing of directories (e.g. exploded deployments) and basic archive formats (jar, war and ear)   
* Package or class based dependency models
* Node weight based on actual code size (i.e. bytecode size)
* Node filters and mappers for basic noise reduction (eg. removing certain packages from the model)
* Basic graph visualisation using *matplotlib*
* Exporting to common graph formats using standard *networkx* facilities (eg. dot, gml or graphml)

Usage
=====

Run the command-line tool (use ``coffea -h`` for a complete list of options)::

    $ coffea -i <directory|jar|war|ear|class>

Example
=======

Modelling `JBoss AS 7.x <http://www.jboss.org/jbossas>`_ internal dependency structure:: 

    $ coffea -p -i /opt/jboss-7.2.0.GA/modules/ -Ip org.jboss. -Mrp org.jboss. -Mep 0 -El logging

Interactive mode equivalent::
    
    >>> from coffea.builder import Builder
    >>> from coffea.analyzer import Plotter
    >>> from coffea.model import NodeIdFilter, NodeIdMapper
    >>> b = Builder()
    >>> b.model.node_filters.append(NodeIdFilter(lambda it: it.startswith('org.jboss.')))
    >>> b.model.node_filters.append(NodeIdMapper(lambda it: it.replace('org.jboss.', '')))
    >>> b.model.node_filters.append(NodeIdMapper(lambda it: it.split('.')[0]))
    >>> b.model.node_filters.append(NodeIdFilter(lambda it: it not in ['logging']))
    >>> b.append('/opt/jboss-7.2.0.GA/modules/')
    No handlers could be found for logger "scanner"
    >>> print len(b.model.nodes)
    48
    >>> p = Plotter(b.model)
    >>> p.plot()
    
    [Displays an interactive view of the dependency model]
    
    >>> p.plot(filename='/tmp/jboss7_module_dependencies.png')

Output:

.. image:: https://github.com/sbilinski/coffea/blob/master/examples/output/jboss_as_7.png
    :alt: JBoss 7.x internal dependencies
    
Unit testing
============

You can run the test suite directly from the command line::

    $ python -m unittest discover


