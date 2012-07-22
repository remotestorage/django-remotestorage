#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from xml.dom.minidom import getDOMImplementation, Node

import itertools as it, operator as op, functools as ft
from collections import namedtuple


Link = namedtuple('Link', 'attributes titles properties')

_node_fields = 'value attributes'
TextNode = namedtuple('TextNode', _node_fields)
Title = namedtuple('Title', _node_fields)
Property = namedtuple('Property', _node_fields)
Property.xsi_nil = True


def force_class(obj, cls):
	if isinstance(obj, dict): obj = cls(None, obj)
	elif isinstance(obj, bytes): obj = cls(obj, dict())
	if not isinstance(obj, cls):
		raise ValueError( 'Passed node object must be either'
			' attribute-dict, bytes value or {} instance: {}'.format(cls, obj) )
	return obj

def node_xrd(obj, cls, doc=None):
	if not isinstance(cls, bytes):
		obj = force_class(obj, cls)
		cls = cls.__name__
	else: obj = TextNode(obj, dict())

	node = doc.createElement(cls)
	for k,v in obj.attributes.viewitems(): node.setAttribute(k, v)
	if obj.value is not None:
		node.appendChild(doc.createTextNode(bytes(obj.value)))
	elif getattr(obj, xsi_nil, False): node.setAttribute('xsi:nil', 'true')

	return node

def node_jrd(obj):
	if isinstance(obj, bytes): return obj
	elif isinstance(obj, dict): return None
	else: return obj.value


xrd_base_attributes = dict(xmlns='http://docs.oasis-open.org/ns/xri/xrd-1.0')

def generate_xrd(
		links=list(), properties=list(), aliases=list(), elements=dict(),
		attributes=xrd_base_attributes ):
	doc = getDOMImplementation().createDocument(attributes['xmlns'], 'XRD', None)
	root = doc.documentElement
	doc_node = ft.partial(node_xrd, doc=doc)

	for k,v in xrd_base_attributes.viewitems(): root.setAttribute(k, v)

	for k,v in elements.viewitems(): root.appendChild(doc_node(v, k))
	for alias in aliases: root.appendChild(doc_node(v, 'Alias'))
	for v in properties: root.appendChild(doc_node(v, Property))

	for link in links:
		node = doc.createElement('Link')
		if link.attributes.get('href') and link.attributes.get('template'):
			raise ValueError( 'Only one of "href" or "template"'
				' attributes may be specified for link: {}'.format(link) )
		for k,v in link.attributes.viewitems(): node.setAttribute(k, v)
		for v in link.titles or list(): node.appendChild(doc_node(v, Title))
		for v in link.properties or list(): node.appendChild(doc_node(v, Property))
		root.appendChild(node)

	return doc


def generate_jrd(
		links=list(), properties=list(), aliases=list(), elements=dict(),
		attributes=xrd_base_attributes ):
	# Based on http://hueniverse.com/2010/05/jrd-the-other-resource-descriptor/
	doc = dict()

	def append_props(node, properties):
		for prop in properties:
			prop = force_class(prop, Property)
			if 'type' not in prop.attributes or prop.value is None: continue
			if 'properties' not in node: node['properties'] = dict()
			node['properties'][prop.attributes['type']] = prop.value

	doc.update(elements)
	append_props(doc, properties)
	if aliases: doc['aliases'] = aliases

	doc_links = doc['links'] = list()
	for link in links:
		doc_link = link.attributes.copy()
		doc_links.append(doc_link)
		for title in link.titles:
			title = force_class(title, Title)
			if 'xml:lang' not in title.attributes:
				if title.value is not None: doc_link['title'] = title.value
				continue
			if title.value is not None:
				if 'titles' not in doc_link: doc_link['titles'] = dict()
				doc_link['titles'][title.attributes['xml:lang']] = title.value
		append_props(doc_link, link.properties)

	return doc
