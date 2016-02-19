import datetime
import decimal
import unittest
import uuid

import typing
from marshmallow import fields, Schema

from lymph.schema.decorator import spec


def _dummy():
    pass


class FancyString(fields.String):
    pass


class NestedSchema(Schema):
    id = fields.UUID(missing=lambda: str(uuid.uuid4()))
    name = fields.String(required=True)


class OtherSchema(Schema):
    name = FancyString()


class ExampleSchema(Schema):
    id = fields.UUID(missing=lambda: str(uuid.uuid4()))
    name = FancyString()
    price = fields.Decimal(required=True)
    pricy = fields.Decimal(load_from='price', dump_to='pricey')
    quantity = fields.Integer(missing=1)
    simple_list = fields.Nested(NestedSchema, many=True)
    simple = fields.Nested(NestedSchema, required=True)
    simple_self = fields.Nested('self', only=('id', 'price'), many=False)
    simple_self_list = fields.Nested('self', only=('id', 'price'), many=True)
    complex_self_list = fields.Nested('self', exclude=('pricy', 'simple_self', 'simple_self_list', 'complex_self_list', 'simple_list', 'simple'), many=True)


class DecoratorTest(unittest.TestCase):
    maxDiff = None

    def test_returns(self):
        results = {
            int: {'type': 'number', 'format': 'integer'},
            float: {'type': 'number', 'format': 'float'},
            decimal.Decimal: {'type': 'string', 'format': 'decimal'},
            uuid.UUID: {'type': 'string', 'format': 'uuid'},
            datetime.datetime: {'type': 'string', 'format': 'date-time'},
            datetime.date: {'type': 'string', 'format': 'date'},
            datetime.time: {'type': 'string', 'format': 'time'},
            dict: {'type': 'object'},
            str: {'type': 'string'},
            unicode: {'type': 'string'},
            None: {'type': 'null'},
            list: {'type': 'array'},
            bool: {'type': 'boolean'},
            typing.List[str]: {'type': 'array', 'items': {'type': 'string'}},
            typing.List[OtherSchema]: {'type': 'array', 'items': {
                'properties': {
                    'name': {'title': 'name', 'type': 'string'},
                },
                'required': [],
                'type': 'object'
            }},
            ExampleSchema(): {
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
                    'simple_self_list': {
                        'type': ['array', 'null'],
                        'items': {
                            'properties': {
                                'id': {'title': 'id', 'type': 'string', 'format': 'uuid'},
                                'price': {'title': 'price', 'type': 'number', 'format': 'decimal'},
                            },
                            'required': ['price'],
                            'type': 'object'
                        },
                    },
                    'simple_self': {
                        'type': 'object',
                        'properties': {
                            'id': {'format': 'uuid', 'title': 'id', 'type': 'string'},
                            'price': {'format': 'decimal', 'title': 'price', 'type': 'number'}
                        },
                        'required': ['price'],
                    },
                    'complex_self_list': {
                        'type': ['array', 'null'],
                        'items': {
                            'properties': {
                                'id': {'title': 'id', 'type': 'string', 'format': 'uuid'},
                                'price': {'title': 'price', 'type': 'number', 'format': 'decimal'},
                                'name': {'title': 'name', 'type': 'string'},
                                'quantity': {'title': 'quantity', 'type': 'number', 'format': 'integer'},
                            },
                            'required': ['price'],
                            'type': 'object'
                        },
                    },
                    'name': {'title': 'name', 'type': 'string'},
                    'price': {'title': 'price', 'type': 'number', 'format': 'decimal'},
                    'pricey': {'title': 'pricy', 'type': 'number', 'format': 'decimal'},
                    'quantity': {'title': 'quantity', 'type': 'number', 'format': 'integer'},
                },
                'required': ['price', 'simple'],
            }
        }

        for in_, out in results.items():
            spec(returns=in_)(_dummy)
            self.assertEqual(_dummy.__annotations__['return'], out)

    def test_unsupported_type(self):
        class A(object):
            pass

        with self.assertRaises(ValueError):
            spec(returns=A)(_dummy)

