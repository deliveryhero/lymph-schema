import collections
import datetime
import decimal
import unittest
import uuid

import six

from lymph.schema.message import build


class MessageTest(unittest.TestCase):
    def test_simple_python_types(self):
        schema = {
            'users': {
                '1.0.1': {
                    'methods': {
                        'get': {
                            'returns': {},
                        },
                    },
                },
            },
        }

        results = {
            int: {'type': 'number', 'format': 'integer'},
            float: {'type': 'number', 'format': 'float'},
            decimal.Decimal: {'type': 'string', 'format': 'decimal'},
            uuid.UUID: {'type': 'string', 'format': 'uuid'},
            datetime.datetime: {'type': 'string', 'format': 'date-time'},
            datetime.date: {'type': 'string', 'format': 'date'},
            datetime.time: {'type': 'string', 'format': 'time'},
            dict: {'type': 'object'},
            six.text_type: {'type': 'string'},
            unicode: {'type': 'string'},
            type(None): {'type': 'null'},
            list: {'type': 'array'},
            bool: {'type': 'boolean'},
        }

        for out, in_ in results.items():
            schema['users']['1.0.1']['methods']['get']['returns'] = in_
            msg = build(schema, 'users@1.0.1', 'get')

            self.assertTrue(isinstance(msg, out))

    def test_complex_schema(self):
        returns = {
            'type': 'object',
            'properties': {
                'id': {'title': 'id', 'type': 'string', 'format': 'uuid'},
                'simple_list': {
                    'type': ['array', 'null'],
                    'items': {
                        'properties': {
                            'id': {'title': 'id', 'type': 'string', 'format': 'uuid'},
                            'name': {'title': 'name', 'type': 'string'},
                        },
                        'required': ['name'],
                        'type': 'object'
                    },
                },
                'simple': {
                    'type': 'object',
                    'properties': {
                        'name': {'title': 'name', 'type': 'string'},
                        'id': {'title': 'id', 'type': 'string', 'format': 'uuid'},
                    },
                    'required': ['name'],
                },
                'name': {'title': 'name', 'type': 'string'},
                'price': {'title': 'price', 'type': 'number', 'format': 'decimal'},
                'quantity': {'title': 'quantity', 'type': 'number', 'format': 'integer'},
            },
            'required': ['price', 'simple'],
        }

        schema = {
            'users': {
                '1.0.1': {
                    'methods': {
                        'get': {
                            'returns': returns,
                        },
                    },
                },
            },
        }

        msg = build(schema, 'users@1.0.1', 'get')

        self.assertTrue(isinstance(msg, collections.Mapping))

    def test_unknown_service(self):
        schema = {
            'users': {
                '1.0.1': {
                    'methods': {
                        'get': {
                            'returns': {'type': 'string'},
                        },
                    },
                },
            },
        }

        with self.assertRaises(ValueError):
            build(schema, 'users@0.1.0', 'get')

    def test_unknown_method(self):
        schema = {
            'users': {
                '1.0.1': {
                    'methods': {
                        'get': {
                            'returns': {'type': 'string'},
                        },
                    },
                },
            },
        }

        with self.assertRaises(ValueError):
            build(schema, 'users@1.0.1', 'unknown')

    def test_no_returns(self):
        schema = {
            'users': {
                '1.0.1': {
                    'methods': {
                        'get': {
                            'returns': {},
                        },
                    },
                },
            },
        }

        with self.assertRaises(ValueError):
            build(schema, 'users@1.0.1', 'get')
