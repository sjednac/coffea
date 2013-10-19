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
import os
import re
import shutil
import sys
import tempfile
import zipfile

_PATTERN_ALL_SUPPORTED = ".*\.(class|jar|war|ear)$"
_PATTERN_ARCHIVE       = ".*\.(jar|war|ear)$"
 
log = logging.getLogger('scanner')

class JavaScanner(object):
    """A simple Java artifact provider."""

    def __init__(self, callback):
        """Initializes a new instance of the JavaScanner class."""
        self._work_dir = tempfile.mkdtemp()
        self.callback = callback
         
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.dispose()

    def dispose(self):
        """Removes accumulated temporary files."""
        shutil.rmtree(self._work_dir)
        
    def supported_file(self, path):
        """Checks if specified file can be consumed by this scanner."""
        
        if not os.path.isfile(path):
            raise AssertionError('Regular file expected: %s' % path)
    
        if not re.match(_PATTERN_ALL_SUPPORTED, path):
            return False
        
        #TODO: Additional filters (skip selected libraries for example)
        return True 
    
    def scan(self, root):
        """Scans specified directory for selected Java artifacts."""
        
        log.info('Scanning: root=%s', root)

        # TODO: Iterative implementation + archive stack (ability to resolve class origin)
        classes = 0
        if os.path.isfile(root):
            if self.supported_file(root):
                classes += self._process_artifact(root)
        elif os.path.isdir(root):
            for dirpath, dirnames, filenames in os.walk(root):
                for f in filenames:
                    path = os.path.join(dirpath, f)
                    if self.supported_file(path):
                        classes += self._process_artifact(path)
        else:
            raise AssertionError('Directory or a regular file expected: %s' % root)

        return classes 

    def _process_artifact(self, path):
        if re.match(_PATTERN_ARCHIVE, path):
            archive_dir = self._unpack(path)
            if archive_dir == None:
                # Don't process, if it's a duplicate
                return 0

            return self.scan(archive_dir)
        else:
            assert path.endswith('.class')
            self._process_class(path)
            return 1

    def _process_class(self, path):
        if self.callback is None:
            raise AssertionError('Invalid callback.')
        self.callback(path)

    def _unpack(self, path):
        basename = os.path.basename(path)
        target_dir = os.path.join(self._work_dir, basename)
       
        if os.path.isdir(target_dir):
            log.warn('Duplicate library: %s', basename)
            return None

        archive = zipfile.ZipFile(path)
        try:
            log.info('Extracting: %s to %s', basename, target_dir) 
            archive.extractall(target_dir)
        finally:
            archive.close()
        
        return target_dir


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage %s <class|jar|war|ear|root_dir>\n' % __file__)
        sys.exit(1)

    target_path = sys.argv[1]
    if not os.path.exists(target_path):
        sys.stderr.write('Target not found: %s\n' % target_path)
        sys.exit(2)

    def print_result_callback(path): 
        print path

    with JavaScanner(print_result_callback) as scanner:
        scanner.scan(target_path)
