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

""" Class Wsdl to generate WSDL Document """
from __future__ import unicode_literals
from builtins import object
import xml.dom.minidom
import inspect
from tornadows import xmltypes
from tornadows import complextypes

class Wsdl(object):
	""" ToDO:
		- Incorporate exceptions for parameters inputs.
		- When elementInput and/or elementOutput are empty trigger a exception.
	"""
	def __init__(self,nameservice=None,targetNamespace=None,arguments=None,elementInput=(),elementOutput=(),operation=None,location=None):
		self._nameservice = nameservice
		self._namespace = targetNamespace
		self._arguments = arguments
		self._elementNameInput = elementInput[0]
		self._elementInput = elementInput[1]
		self._elementNameOutput = elementOutput[0]
		self._elementOutput = elementOutput[1]
		self._operation = operation
		self._location = location

	def createWsdl(self):
		typeInput  = None
		typeOutput = None
		types  = '<wsdl:types>\n'
		types += '<xsd:schema targetNamespace="%s">\n'%self._namespace

		if inspect.isclass(self._elementInput) and issubclass(self._elementInput,complextypes.ComplexType):
			typeInput = self._elementInput.getName()
			types += self._elementInput.toXSD()
		elif isinstance(self._elementInput,dict):
			typeInput = self._elementNameInput
			types += self._createComplexTypes(self._elementNameInput, self._arguments, self._elementInput)
		elif isinstance(self._elementInput,xmltypes.Array):
			typeInput  = self._elementNameInput
			types += self._elementInput.createArray(typeInput)
		elif isinstance(self._elementInput,list) or issubclass(self._elementInput,xmltypes.PrimitiveType):
			typeInput  = self._elementNameInput
			types += self._createTypes(typeInput,self._elementInput)

		if inspect.isclass(self._elementOutput) and issubclass(self._elementOutput,complextypes.ComplexType):
			typeOutput = self._elementOutput.getName()
			types += self._elementOutput.toXSD()
		elif isinstance(self._elementOutput,xmltypes.Array):
			typeOutput = self._elementNameOutput
			types += self._elementOutput.createArray(typeOutput)
		elif isinstance(self._elementOutput,list) or issubclass(self._elementOutput,xmltypes.PrimitiveType):
			typeOutput = self._elementNameOutput
			types += self._createTypes(typeOutput,self._elementOutput)

		types += '</xsd:schema>\n'
		types += '</wsdl:types>\n'
		messages  = '<wsdl:message name="%sRequest">\n'%self._nameservice
		messages += '<wsdl:part name="parameters" element="tns:%s"/>\n'%typeInput
		messages += '</wsdl:message>\n'
		messages += '<wsdl:message name="%sResponse">\n'%self._nameservice
		messages += '<wsdl:part name="parameters" element="tns:%s"/>\n'%typeOutput
		messages += '</wsdl:message>\n'
		portType  = '<wsdl:portType name="%sPortType">\n'%self._nameservice
		portType += '<wsdl:operation name="%s">\n'%self._operation
		portType += '<wsdl:input message="tns:%sRequest"/>\n'%self._nameservice
		portType += '<wsdl:output message="tns:%sResponse"/>\n'%self._nameservice
		portType += '</wsdl:operation>\n'
		portType += '</wsdl:portType>\n'
		binding  = '<wsdl:binding name="%sBinding" type="tns:%sPortType">\n'%(self._nameservice,self._nameservice)
		binding += '<soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>\n'
		binding += '<wsdl:operation name="%s">\n'%self._operation
		binding += '<soap:operation soapAction="%s" style="document"/>\n'%self._location
		binding += '<wsdl:input><soap:body use="literal"/></wsdl:input>\n'
		binding += '<wsdl:output><soap:body use="literal"/></wsdl:output>\n'
		binding += '</wsdl:operation>\n'
		binding += '</wsdl:binding>\n'
		service  = '<wsdl:service name="%s">\n'%self._nameservice
		service += '<wsdl:port name="%sPort" binding="tns:%sBinding">\n'%(self._nameservice,self._nameservice)
		service += '<soap:address location="%s"/>\n'%self._location
		service += '</wsdl:port>\n'
		service += '</wsdl:service>\n'

		definitions  = '<wsdl:definitions name="%s"\n'%self._nameservice
		definitions  += 'xmlns:xsd="http://www.w3.org/2001/XMLSchema"\n'
		definitions  += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
		definitions  += 'xmlns:tns="%s"\n'%self._namespace
		definitions  += 'xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"\n'
		definitions  += 'xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"\n'
		definitions  += 'targetNamespace="%s">\n'%self._namespace
		definitions += types
		definitions += messages
		definitions += portType
		definitions += binding
		definitions += service
		definitions += '</wsdl:definitions>\n'
		wsdlXml = xml.dom.minidom.parseString(definitions)

		return wsdlXml

	def _createTypes(self, name, elements):
		elem = b''
		if isinstance(elements,list):
			elem = b'<xsd:complexType name="%sParams">\n'%name
			elem += b'<xsd:sequence>\n'
			elems = b''
			idx = 1
			for e in elements:
				elems += e.createElement('value%s'%idx)+'\n'
				idx += 1
			elem += elems+b'</xsd:sequence>\n'
			elem += b'</xsd:complexType>\n'
			elem += b'<xsd:element name="%s" type="tns:%sParams"/>\n'%(name,name)
		elif issubclass(elements,xmltypes.PrimitiveType):
			elem = elements.createElement(name)+'\n'

		return elem

	def _createComplexTypes(self, name, arguments, elements):
		elem = b''
		if isinstance(elements,dict):
			elem = b'<xsd:complexType name="%sTypes">\n'%name
			elem += b'<xsd:sequence>\n'
			elems = b''
			for e in arguments:
				if  isinstance(elements[e],xmltypes.Array):
					elems += elements[e].createType(e)
				elif issubclass(elements[e],xmltypes.PrimitiveType):
					elems += elements[e].createElement(e)+'\n'
			elem += elems+b'</xsd:sequence>\n'
			elem += b'</xsd:complexType>\n'
			elem += b'<xsd:element name="%s" type="tns:%sTypes"/>\n'%(name,name)
		elif issubclass(elements,xmltypes.PrimitiveType):
			elem = elements.createElement(name)+'\n'

		return elem
