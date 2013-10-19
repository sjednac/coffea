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

import itertools
import logging
import struct
import sys

from collections import namedtuple

log = logging.getLogger('java')

# Class access flags
_CLASS_ACC_PUBLIC       = 0x0001
_CLASS_ACC_FINAL        = 0x0010
_CLASS_ACC_SUPER        = 0x0020
_CLASS_ACC_INTERFACE    = 0x0200
_CLASS_ACC_ABSTRACT     = 0x0400
_CLASS_ACC_SYNTHETIC    = 0x1000
_CLASS_ACC_ANNOTATION   = 0x2000
_CLASS_ACC_ENUM         = 0x4000

# Constant pool tags
_CONSTANT_Class = 7
_CONSTANT_FieldRef = 9
_CONSTANT_MethodRef = 10
_CONSTANT_InterfaceMethodRef = 11
_CONSTANT_String = 8
_CONSTANT_Integer = 3
_CONSTANT_Float = 4 
_CONSTANT_Long = 5 
_CONSTANT_Double = 6 
_CONSTANT_NameAndType = 12
_CONSTANT_Utf8 = 1
_CONSTANT_MethodHandle = 15
_CONSTANT_MethodType = 16
_CONSTANT_InvokeDynamic = 18

# Constant pool tuples
CPClass = namedtuple('CPClass', 'tag name_index')
CPFieldRef = namedtuple('CPFieldRef', 'tag class_index name_and_type_index')
CPMethodRef = namedtuple('CPMethodRef', 'tag class_index name_and_type_index')
CPInterfaceMethodRef = namedtuple('CPInterfaceMethodRef', 'tag class_index name_and_type_index')
CPString = namedtuple('CPString', 'tag string_index')
CPInteger = namedtuple('CPInteger', 'tag int_bytes')
CPFloat = namedtuple('CPFloat', 'tag float_bytes')
CPLong = namedtuple('CPLong', 'tag high_bytes low_bytes')
CPDouble = namedtuple('CPDouble', 'tag high_bytes low_bytes')
CPNameAndType = namedtuple('CPNameAndType', 'tag name_index descriptor_index')
CPUtf8 = namedtuple('CPUtf8', 'tag utf8_str_len utf8_str')
CPMethodHandle = namedtuple('CPMethodHandle', 'tag reference_kind reference_index')
CPMethodType = namedtuple('CPMethodType', 'tag descriptor_index')
CPInvokeDynamic = namedtuple('CPInvokeDynamic', 'tag bootstrap_method_attr_index name_and_type_index')

# Fields
Field = namedtuple('Field', 'name descriptor attrs')

# Methods
Method = namedtuple('Method', 'name descriptor attrs')
Code = namedtuple('Code', 'length')

# Attributes
Attribute = namedtuple('Attribute', 'name value')

class JavaClass(object):
    """A Python representation of a Java class."""
    
    def __init__(self, filename):
        """Creates a new object instance using a .class file as input."""
        self._parse(filename)

    def __repr__(self):
        """Returns a string representation of this object."""
        str = "JavaClass: "
        if self.public:
            str += "public "
        if self.final: 
            str += "final "
        elif self.abstract:
            str += "abstract "

        if self.interface:
            str += "interface "
        elif self.annotation:
            str += "annotation "  
        elif self.enum:
            str += "enum "
        else: 
            str += "class "

        str += self.name 
        if self.super_name != 'java/lang/Object':
            str += " extends "
            str += self.super_name

        if len(self.interfaces) > 0:
            str += " implements " + ','.join(self.interfaces)

        return str

    def _parse(self, filename):
        """Main parse method."""    
        log.debug('Processing bytecode: %s', filename)
        with open(filename, "rb") as f:
            self._parse_header(f)
            self._parse_constant_pool(f)
            self._parse_class_declaration(f)
            self._parse_fields(f)
            self._parse_methods(f)
            self._parse_attributes(f)

    def _parse_header(self, f):
        """Parse header: magic, minor, major."""
        (magic,) = struct.unpack('>I', f.read(4))
        if magic != 0xcafebabe:
            raise AssertionError('Invalid class header: magic={0} file={1}'.format(hex(magic), f.name))
        (self.minor, self.major) = struct.unpack('>HH', f.read(4))
        log.debug('Header: magic=%s minor=%d major=%d', hex(magic), self.minor, self.major)

    def _parse_constant_pool(self, f):
        """Parse the constant pool."""
        (constant_pool_count,) = struct.unpack('>H', f.read(2))
        log.debug('Constant pool count: %d', constant_pool_count)       

        #All 8-byte constants (long, double) take up two entries in the constant_pool (skip one entry)
        def _skip_one(iterator):       
                next(itertools.islice(iterator, 1, 1), None)
                # Keep the index consistent - add an empty entry to fill in the gap
                self.constant_pool.append(None)

        # Constant pool index starts at 1 - assume an empty reference at 0  
        self.constant_pool = [None]
        cp_iterator = iter(xrange(1, constant_pool_count))
        for cp_index in cp_iterator:
            (tag,) = struct.unpack('>B', f.read(1))
            if tag == _CONSTANT_Class:
                cp_item = CPClass(tag, *struct.unpack('>H', f.read(2)))             
            elif tag == _CONSTANT_FieldRef:
                cp_item = CPFieldRef(tag, *struct.unpack('>HH', f.read(4)))
            elif tag == _CONSTANT_MethodRef:
                cp_item = CPMethodRef(tag, *struct.unpack('>HH', f.read(4)))
            elif tag == _CONSTANT_InterfaceMethodRef:
                cp_item = CPInterfaceMethodRef(tag, *struct.unpack('>HH', f.read(4)))
            elif tag == _CONSTANT_String:
                cp_item = CPString(tag, *struct.unpack('>H', f.read(2)))
            elif tag == _CONSTANT_Integer:
                cp_item = CPInteger(tag, *struct.unpack('>I', f.read(4)))
            elif tag == _CONSTANT_Float:
                cp_item = CPFloat(tag, *struct.unpack('>I', f.read(4)))
            elif tag == _CONSTANT_Long:
                cp_item = CPLong(tag, *struct.unpack('>II', f.read(8)))
                _skip_one(cp_iterator)
            elif tag == _CONSTANT_Double:
                cp_item = CPDouble(tag, *struct.unpack('>II', f.read(8)))
                _skip_one(cp_iterator)
            elif tag == _CONSTANT_NameAndType:
                cp_item = CPNameAndType(tag, *struct.unpack('>HH', f.read(4)))
            elif tag == _CONSTANT_Utf8:
                (utf8_str_len,) = struct.unpack('>H', f.read(2))
                cp_item = CPUtf8(tag, utf8_str_len, *struct.unpack(str(utf8_str_len)+'s', f.read(utf8_str_len)))    
            elif tag == _CONSTANT_MethodHandle:
                #FIXME: Implement MethodHandle parser
                raise AssertionError('Not implemented: MethodHandle!')
            elif tag == _CONSTANT_MethodType:
                #FIXME: Implement MethodType parser
                raise AssertionError('Not implemented: MethodType!')
            elif tag == _CONSTANT_InvokeDynamic:
                #FIXME: Implement InvokeDynamic parser
                raise AssertionError('Not implemented: InvokeDynamic!')
            else:
                log.error('Unknown tag: %d', tag)
                raise AssertionError('Unknown tag: {0}'.format(tag))
            
            self.constant_pool.append(cp_item)

    def _parse_class_declaration(self, f):
        """Parse class declaration: access flags, this/super class, implemented interfaces."""
        (access_flags, this_class, super_class, interface_count) = struct.unpack('>HHHH', f.read(8))
        
        self.public = access_flags & _CLASS_ACC_PUBLIC
        self.final = access_flags & _CLASS_ACC_FINAL
        self.interface = access_flags & _CLASS_ACC_INTERFACE
        self.abstract = access_flags & _CLASS_ACC_ABSTRACT
        self.annotation = access_flags & _CLASS_ACC_ANNOTATION
        self.enum = access_flags & _CLASS_ACC_ENUM 

        self.name = self._constant_pool_class(this_class)
        self.super_name = self._constant_pool_class(super_class)
        self.interfaces = []
        for interface_index in xrange(interface_count):
            (interface_cp_index, ) = struct.unpack('>H', f.read(2))
            interface_class = self._constant_pool_class(interface_cp_index) 
            self.interfaces.append(interface_class)

        self.package = '.'.join(self.name.split('.')[:-1])

    def _parse_fields(self, f):
        """Parse class fields."""
        (fields_count,) = struct.unpack('>H', f.read(2))
        self.fields = []
        for field_index in xrange(fields_count):
            (access_flags, name_index, descriptor_index, attributes_count) = struct.unpack('>HHHH', f.read(8))
            
            field = Field(self._constant_pool_name(name_index), self._constant_pool_name(descriptor_index), [])
            for attribute_index in xrange(attributes_count):
                field.attrs.append(self._parse_attribute_info(f))
            
            self.fields.append(field)
            log.debug('Field: %s %s %s', field.name, field.descriptor, field.attrs)

    def _parse_methods(self, f):
        """Parse class methods."""
        (methods_count,) = struct.unpack('>H', f.read(2))
        self.methods = []
        for method_index in xrange(methods_count):
            (access_flags, name_index, descriptor_index, attributes_count) = struct.unpack('>HHHH', f.read(8))
            
            method = Method(self._constant_pool_name(name_index), self._constant_pool_name(descriptor_index), [])
            for attribute_index in xrange(attributes_count):
                method.attrs.append(self._parse_attribute_info(f))
            
            self.methods.append(method)
            log.debug('Method: %s %s %s', method.name, method.descriptor, method.attrs)


    def _parse_attributes(self, f):
        """Parse class attributes."""
        (attributes_count,) = struct.unpack('>H', f.read(2))
        self.attributes = []
        for attribute_index in xrange(attributes_count):
            self.attributes.append(self._parse_attribute_info(f))
        
        if log.isEnabledFor(logging.DEBUG):
            log.debug('Attributes: %s', map(lambda it: it.name+':'+str(it.value), self.attributes))


    def _parse_attribute_info(self, f):
        """Parse attribute info. """
        (attribute_name_index, attribute_length) = struct.unpack('>HI', f.read(6))

        attr_name = self._constant_pool_name(attribute_name_index)
        if attr_name == 'SourceFile':
            attr_value = self._constant_pool_name(*struct.unpack('>H', f.read(2)))
        elif attr_name == 'Deprecated':
            attr_value = True
        elif attr_name == 'Code':
            f.read(attribute_length) 
            attr_value = Code(attribute_length)
        elif attr_name == 'Signature':
            attr_value = self._constant_pool_name(*struct.unpack('>H', f.read(2)))
        elif attr_name == 'Exceptions':
            attr_value = []
            for exception_index in xrange(*struct.unpack('>H', f.read(2))):
                exception_class = self._constant_pool_class(*struct.unpack('>H', f.read(2)))
                attr_value.append(exception_class)
        else:
            # Skip unsupported content
            # TODO: Debug, since most aren't supported at this point
            log.debug('(!) Unknown attribute: %s', attr_name)             
            f.read(attribute_length)
            attr_value = None

        return Attribute(attr_name, attr_value)

    def _constant_pool_class(self, class_index):
        """Gets a class name from the constant pool."""
        return self._constant_pool_name(self.constant_pool[class_index].name_index).replace('/', '.')

    def _constant_pool_name(self, name_index):
        """Gets a name from the constant pool."""
        return self.constant_pool[name_index].utf8_str

    def class_dependencies(self, sort=True):
        """Returns a set of class dependencies."""
        class_defs = []
        for cd in filter(lambda it: it and it.tag == _CONSTANT_Class, self.constant_pool):
            class_name = self._constant_pool_name(cd.name_index)
            if class_name[0] == '[':
                array_dim = class_name.count('[')
                if array_dim > 0:
                    class_name = class_name[array_dim+1:]
            
            if len(class_name) > 0 and class_name[-1] == ';':
                class_name = class_name[:-1]
            
            class_name = class_name.replace('/', '.')    
            if class_name not in class_defs:
                class_defs.append(class_name)
            
        return sorted(class_defs) if sort else class_defs
    
    def package_dependencies(self, sort=True):
        """Returns a set of package dependencies."""
        pkg_defs = set(map(lambda it: '.'.join(it.split('.')[:-1]), self.class_dependencies(sort=False)))
        return sorted(pkg_defs) if sort else pkg_defs
        
