lymph-schema
============

A toolkit to translate lymph service interfaces to machine-readeable schemas
(and potentially vice versa)

Interface definitions
---------------------

lymph-schema allows developers to generate a programmable schema from a
service's interface.

Schema
~~~~~~

A schema is a representation of lymph service's RPC interfaces.

Example ::

    {
        "orders": {
             "0.1.0": {
                 "methods": {
                     "submit": {
                         "args": ["values"],
                         "kwargs": {},
                         "doc": "Submit an order",
                         "raises": ["ValidationError"],
                         "returns": {"type": "number", "format": "integer"}
                     },
                     "get": {
                         "args": ["id"],
                         "kwargs": {"name": ""},
                         "doc": "Get an order",
                         "raises": ["NotFound"],
                         "returns": {
                             "title": "OrderSchema",
                             "type": "object",
                             "properties": {
                               "name": {"type": "string"}
                             }
                         }
                     }
                 }
             }
        }
    }

Note: We use json-schema (http://json-schema.org/) to represent returns of
RPC methods.

Interface instrumentation
~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes we need to annotate our interfaces for better schemas. To get the
schema from above the service's interface should look like this:

::

    import lymph

    from lymph.schema.decorator import spec


    class Orders(lymph.Interface):
         @lymph.rpc(raises=NotFound)
         @spec(returns=OrderSchema)
         def get(self, id, name=""):
             "Get an order"
             # Code ...

         @lymph.rpc(raises=ValidationError)
         @spec(returns=int)
         def submit(self, values):
             "Submit an order"
             # Code ...


Note: Because of dynamic typing in Python we need to inform lymph-schema about
the return type of an RPC function. This's what the ``@spec`` decorator allow
us to do.

Command line
~~~~~~~~~~~~

To generate a schema from a service configuration on the command line do:

::

    lymph schema-gen conf/orders.yml
    {
        "orders": ...
    }


Programmatically
~~~~~~~~~~~~~~~~

To generate schema programmatically do:

::

    from lymph.schema import generator

    from lymph.orders.interfaces import Orders


    generator.generate(Orders, 'orders@0.1.0')


Exposing schema via RPC
~~~~~~~~~~~~~~~~~~~~~~~

To expose a schema via RPC do:

::

    import lymph
    from lymph.schema import generator
    from lymph.schema.decorator import spec


    class Orders(lymph.Interface):

        @lymph.rpc()
        @spec(returns=dict)
        def get_schema(self):
            return generator.generate_from_interface(self)


Complex return types
--------------------

To expose more complex types we use the
typing(https://pypi.python.org/pypi/typing) library as you can see here:

::

    import uuid

    import typing
    import lymph
    from lymph.schema import generator
    from lymph.schema.decorator import spec


    class Orders(lymph.Interface):

        @lymph.rpc()
        @spec(returns=typing.List[uuid.UUID])
        def search(self):
            return [uuid.uuid4() for _ in range(3)]


Testing
-------

One of the use cases of a programmable schema is to be able to write good unit
tests such that the consumer is decoupled from its producer.

Create Fakes
~~~~~~~~~~~~

lymph-schema can generate fake services as an `hermetic server`_ from a schema
for testing purposes:

::

    from lymph.schema import fake

    orders = fake.build(SCHEMA, "orders@0.1.0")

    print orders.submit(values={"a": 1})


Note: This code will print the same return type as the real interface but
generated randomly.

Consumer unit test
~~~~~~~~~~~~~~~~~~

lymph-schema also contains a toolkit to help writing unit test and extensions
for lymph's mocking helpers with a better API:

::

    from lymph.schema import testcase, Schema


    class TestAPIEndpoint(testcase.MockServiceTester):

         rpc_schema = Schema({...})

         def setUp(self):
             super(TestAPIEndpoint, self).setUp()

             self.mocker.on('orders@0.1.0', 'get').returns({'name': 'foo'})
             self.mocker.on('orders@0.1.0', 'submit').raises(ValueError)

        def test_some_endpoint(self):
            # Do some stuff ...

            self.assert_not_called('orders@0.1.0', 'get', values={})

            # Assert called any number of times >= 1.
            self.assert_called('orders', 'submit', id=1)


.. _hermetic server: http://googletesting.blogspot.ch/2012/10/hermetic-servers.html
