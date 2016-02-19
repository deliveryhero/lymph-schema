import datetime
import decimal
import uuid

import six
import typing
import marshmallow

from lymph.schema import _jsonschema


# TODO: Add support of passing jsonschema directly.
# TODO: Allow to annotate function argument too.
# @spec(returns=int, values=dict)
# def create(self, values): pass
def spec(returns):
    """Annotate an RPC function with return type.

    This decorator is only needed with Python 2.x, with Python 3.x
    use function annotations PEP-3107.

    Usage in Python 2.x:

         class Echo(lymph.Interface):
             @lymph.rpc()
             @spec(returns=str)
             def echo(self, text):
                 return text

    Equivalent example in Python 3.x:

         class Echo(lymph.Interface):
             @lymph.rpc()
             def echo(self, text) -> str:
                 return text

    The ``spec`` decorator support using ``typing`` library types.

    """
    def wrapper(func):
        func.__annotations__ = {
            'return': _to_jsonschema(returns)
        }
        return func
    return wrapper


# TODO: Add support for typing.Mapping[K, V]
# TODO: For marshmallow schema will be great if we also have field descriptions.
def _to_jsonschema(type_):
    if isinstance(type_, marshmallow.Schema):
        return _jsonschema.dump_schema(type_)
    elif type_ in six.integer_types:
        return {'type': 'number', 'format': 'integer'}
    elif type_ == float:
        return {'type': 'number', 'format': 'float'}
    elif type_ == decimal.Decimal:
        return {'type': 'string', 'format': 'decimal'}
    elif type_ == uuid.UUID:
        return {'type': 'string', 'format': 'uuid'}
    elif type_ == datetime.datetime:
        return {'type': 'string', 'format': 'date-time'}
    elif type_ == datetime.date:
        return {'type': 'string', 'format': 'date'}
    elif type_ == datetime.time:
        return {'type': 'string', 'format': 'time'}
    elif type_ == dict:
        return {'type': 'object'}
    elif type_ == six.text_type or type_ == six.binary_type:
        return {'type': 'string'}
    elif type_ is None:
        return {'type': 'null'}
    elif type_ == list:
        return {'type': 'array'}
    elif type_ == bool:
        return {'type': 'boolean'}
    elif issubclass(type_, typing.MutableSequence[typing.T]):
        items_type = type_.__parameters__[0]
        if issubclass(items_type, marshmallow.Schema):
            items_type = items_type()
        return {
            'type': 'array',
            'items': _to_jsonschema(items_type),
        }
    else:
        raise ValueError('unsupported return type: %s' % type_)
