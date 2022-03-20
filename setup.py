#!/usr/bin/env python
#
# Copyright 2011 Rodrigo Ancavil del Pino
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import unicode_literals
import distutils.core

try:
	import setuptools
except ImportError:
	pass

distutils.core.setup(
	name='tornadows',
	version = '0.9.3',
	packages=['tornadows','demos'],
	author='Innovaser',
	author_email='rancavil@innovaser.cl',
)
