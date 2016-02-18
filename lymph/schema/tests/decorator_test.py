import datetime
import decimal
import unittest
import uuid

import typing
from marshmallow import fields, Schema

from lymph.schema.decorator import spec


def _dummy():
    pass


class NestedSchema(Schema):
    id = fields.UUID(missing=lambda: str(uuid.uuid4()))
    name = fields.String(required=True)


class ExampleSchema(Schema):
    id = fields.UUID(missing=lambda: str(uuid.uuid4()))
    name = fields.String()
    price = fields.Decimal(required=True)
    quantity = fields.Integer(missing=1)
    simple_list = fields.Nested(NestedSchema, many=True)
    simple = fields.Nested(NestedSchema, required=True)


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
                    'name': {'title': 'name', 'type': 'string'},
                    'price': {'title': 'price', 'type': 'number', 'format': 'decimal'},
                    'quantity': {'title': 'quantity', 'type': 'number', 'format': 'integer'},
                },
                'required': ['price', 'simple'],
            }
        }

        for in_, out in results.items():
            spec(returns=in_)(_dummy)
            self.assertEqual(_dummy.__annotations__['return'], out)

    def test_unsupported_type(self):
        class A:
            pass

        with self.assertRaises(ValueError):
            spec(returns=A)(_dummy)

