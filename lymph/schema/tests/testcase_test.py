import decimal
import uuid

import mock
from marshmallow import fields, Schema
import lymph
from lymph.exceptions import RemoteError
from lymph.testing import RPCServiceTestCase

from lymph.schema.decorator import spec
from lymph.schema.generator import generate
from lymph.schema.testcase import MockServiceTester


class ExampleSchema(Schema):
    id = fields.UUID(missing=lambda: str(uuid.uuid4()))
    name = fields.String()
    price = fields.Decimal(required=True)
    quantity = fields.Integer(missing=1)


class A(lymph.Interface):

    @lymph.rpc(raises=ValueError)
    @spec(returns=ExampleSchema())
    def get(self, id):
        return


class B(lymph.Interface):

    a = lymph.proxy('a', version='0.1.0')

    def a_get(self):
        return self.a.get(id=1)


class TestTestCase(RPCServiceTestCase, MockServiceTester):
    service_class = B
    rpc_schema = generate(A, 'a@0.1.0')

    def test_a_get(self):
        self.mocker.on('a@0.1.0', 'get').returns({'price': decimal.Decimal(10)})

        ret = self.service.a_get()

        self.assertEqual(ret, {
            'id': mock.ANY,
            'name': mock.ANY,
            'price': decimal.Decimal(10),
            'quantity': mock.ANY,
        })

        self.assert_called('a', 'get', id=1)

    def test_a_get_raises(self):
        self.mocker.on('a@0.1.0', 'get').raises(ValueError("bla"))

        with self.assertRaises(RemoteError.ValueError):
            self.service.a_get()

        self.assert_called('a', 'get', id=1)

    def test_a_get_not_called(self):
        self.assert_not_called('a', 'get', id=1)

    def test_raises_unsupported_exception(self):
        with self.assertRaises(ValueError):
            self.mocker.on('a@0.1.0', 'get').raises(Exception('bla'))
