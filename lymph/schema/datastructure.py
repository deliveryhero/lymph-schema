import collections
import datetime
import decimal
import uuid


_TYPES = {
    'integer': int,
    'float': float,
    'decimal': decimal.Decimal,
    'date': datetime.datetime.date,
    'time': datetime.time,
    'date-time': datetime.datetime,
    'uuid': uuid.UUID,
    'string': (str, unicode),
    'boolean': bool,
    'object': dict,
    'array': list,
    'null': type(None),
}


# TODO: Figure out how to deal with nested data.
class JsonSchemaDict(collections.MutableMapping):
    """A mapping that adhere to a schema (jsonschema format).

    The mapping should only allow setting keys if the schema have them and
    the values match the same type in the schema.

    This datastructure can become very handy when definining custom messages
    for our rpc function.

    Example:

        >>> properties = {
        ...     'name': {'type': 'string'},
        ...     'age': {'type': 'number', 'format': 'integer'},
        ...     'addresses': {'type': ['array', 'null']},
        ... }
        ...
        >>> d = JsonSchemaDict(properties, {'name': 'joe', 'age': 11, 'addresses': []})
        >>> d['age'] = 12
        >>> d['age']
        12
        >>> d['age'] = 'foo'
        Traceback (most recent call last):
            ...
        TypeError: cannot set 'age' (type <type 'int'>) to 'foo'
        >>> d['new_key'] = 1
        Traceback (most recent call last):
            ...
        KeyError: "unknown key 'new_key'"
        >>> d['addresses'] = None
        >>> len(d)
        3
        >>> sorted(k for k in d)
        ['addresses', 'age', 'name']
        >>> del d['age']

    """

    def __init__(self, properties, values):
        self.__values = values
        self.__properties = properties

    def __setitem__(self, key, value):
        try:
            schema = self.__properties[key]
        except KeyError:
            raise KeyError('unknown key %r' % key)
        self.__check_type_match(key, value, schema)

        self.__values[key] = value

    def __check_type_match(self, key, value, schema):
        # FIXME: How about nested object checking ? object, array ?
        vtype = self.__get_type(value, schema)
        if not isinstance(value, vtype):
            raise TypeError("cannot set %r (type %s) to %r" % (key, vtype, value))

    @staticmethod
    def __get_type(value, schema):
        if 'format' in schema:
            return _TYPES[schema['format']]
        elif 'type' in schema:
            if isinstance(schema['type'], list):
                return tuple(_TYPES[t] for t in schema['type'])
            return _TYPES[schema['type']]
        else:
            raise RuntimeError('malformed schema')

    def __getitem__(self, key):
        return self.__values[key]

    def __delitem__(self, key):
        del self.__values[key]

    def __iter__(self):
        return iter(self.__values)

    def __len__(self):
        return len(self.__values)
