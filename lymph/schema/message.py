import decimal
import functools
import random
import uuid

import faker

from lymph.schema import datastructure


_FAKER = faker.Faker()
_FACTORIES = {
    'integer': lambda: _FAKER.random_int(0, 1000000),
    'decimal': lambda: decimal.Decimal(random.randint(0, 10)),
    'date': lambda: _FAKER.date_time().date(),
    'time': lambda: _FAKER.date_time().time(),
    'date-time': _FAKER.date_time,
    'uuid': uuid.uuid4,
    'string': _FAKER.name,
    'boolean': _FAKER.boolean,
    'float': _FAKER.pyfloat,
    'object': lambda: {_FAKER.name(): _FAKER.name() for _ in range(3)},
    'array': lambda: [_FAKER.name() for _ in range(3)],
    'null': lambda: None
}


class BuilderMixin(object):

    def __init__(self):
        self.__messages = {}

    def set_message(self, func_name, msg):
        self.__messages[func_name] = msg

    def _get_message(self, name, rettype):
        try:
            msg = self.__messages[name]
        except KeyError:
            msg = self.__messages[name] = _build_from_type(rettype)
        return msg


def build(schema, name, method):
    """Build a fake message.

    :param schema: Service schema generated by ``lymph schema-gen``.
    :param name: Name of service.
    :param method: name for the rpc function.

    :return: Data of same type as defined in the 'returns' of the rpc method.

    :raises ValueError: In case given service name or version doesn't exist.

    """
    from lymph.schema.schema import Schema

    if not isinstance(schema, Schema):
        schema = Schema(schema)
    service = schema.build_service(name)

    try:
        meth_spec = service.methods[method]
    except KeyError:
        raise ValueError('unknown method %s for service %s' % (method, name))

    returns = meth_spec['returns']
    if not returns:
        raise ValueError(
            'cannot build message since returns was not set for'
            ' service %s method %s' % (name, method))

    return _build_from_type(returns)


def _build_from_type(returns):
    type_ = returns['type']
    if type_ == 'number':
        format = returns['format']
        fact = _FACTORIES[format]
    elif type_ == 'string':
        if 'format' in returns:
            fact = _FACTORIES[returns['format']]
        else:
            fact = _FACTORIES['string']
    elif type_ == 'object':
        if 'properties' in returns:
            fact = functools.partial(_get_object_factory, returns['properties'])
        else:
            fact = _FACTORIES['object']
    elif type_ == 'array':
        if 'items' in returns:
            items_fact = _build_from_type(returns['items'])
            fact = functools.partial(list, [items_fact() for _ in range(3)])
        else:
            fact = _FACTORIES['array']
    elif isinstance(type_, list):  # e.g. ['array', 'null']
        fact = _FACTORIES[random.choice(type_)]
    else:
        fact = _FACTORIES[type_]

    return fact()


def _get_object_factory(properties):
    msg = {}
    for field, meta in properties.items():
        msg[field] = _build_from_type(meta)
    return datastructure.JsonSchemaDict(properties, msg)
