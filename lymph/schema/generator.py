import collections
import inspect

from lymph.core.versioning import parse_versioned_name
from lymph.config import Configuration
from lymph.utils import import_object

from lymph.schema.schema import Schema


# TODO: Use jsonschema meta schema to define/validate the rpc schema.
# TODO: Add emit (for events emitted).
RPCSpec = collections.namedtuple('RPCSpec', 'name args kwargs doc raises returns')


def generate_from_interface(interface):
    """Generate schema from interface instance."""
    if interface.version:
        name = '%s@%s' % (interface.name, interface.version)
    else:
        name = interface.name
    return generate(interface.__class__, name)


# TODO: Generate schema from multiple configs
def generate_from_config(config_file):
    """Generate schema from config file path."""
    config = Configuration()
    config.load_file(config_file)

    return Schema(_get_interfaces(config))


def _get_interfaces(config):
    interfaces = {}
    for name, attrs in config.get('interfaces', {}).items():
        cls = import_object(attrs['class'])
        schema = generate(cls, name)
        schema = schema.todict()
        for k in schema:
            if k in interfaces:
                interfaces[k].update(schema[k])
            else:
                interfaces[k] = schema[k]
    return interfaces


def generate(cls, name):
    name, version = parse_versioned_name(name)
    return Schema({
        name: {
            str(version or ''): {
                'methods': _get_rpc_methods(cls),
            },
        }
    })


def _get_rpc_methods(obj):
    methods = {}
    for _, meth in obj.methods.items():
        spec = _get_rpc_spec(meth)
        methods[spec.name] = spec._asdict()
    return methods


def _get_rpc_spec(rpc_wrapper):
    meth = rpc_wrapper.original
    args, kwargs = _get_args(meth)
    raises = _get_raises(rpc_wrapper)
    returns = _get_returns(meth)

    return RPCSpec(
        name=meth.__name__,
        args=args[1:],   # Skip self.
        kwargs=kwargs,
        doc=meth.__doc__ or '',
        raises=[r.__name__ for r in raises],
        returns=returns,
    )


def _get_args(f):
    """Extract argument positional and optional from function.

    Note:
        Doesn't work with variadic argument style e.g. *args, **kwargs.

    Example:

        >>> def f(a, b, c, d=1, e=2):
        ...     pass
        ...
        >>> _get_args(f) == (['a', 'b', 'c'], {'d': 1, 'e': 2})
        True

        >>> def g(a):
        ...     pass
        ...
        >>> _get_args(g)
        (['a'], {})
        >>> def h():
        ...     pass
        ...
        >>> _get_args(h)
        ([], {})

        >>> def e(*args):
        ...     pass
        ...
        >>> _get_args(e)
        Traceback (most recent call last):
            ...
        ValueError: unsupported function type
        >>> def j(**kwargs):
        ...     pass
        ...
        >>> _get_args(j)
        Traceback (most recent call last):
            ...
        ValueError: unsupported function type

    """
    spec = inspect.getargspec(f)
    if spec.varargs or spec.keywords:
        raise ValueError("unsupported function type")
    defaults = spec.defaults or []
    pos_offset = len(defaults)
    args = spec.args[:len(spec.args) - pos_offset]
    kwargs = {a: v for a, v in zip(spec.args[len(spec.args) - pos_offset:], defaults)}

    return args, kwargs


def _get_returns(f):
    if hasattr(f, '__annotations__'):
        return f.__annotations__.get('return', {})
    return {}


def _get_raises(f):
    raises = getattr(f, 'raises', ())
    if not isinstance(raises, tuple):
        raises = (raises, )
    return raises
