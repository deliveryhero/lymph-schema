from semantic_version import Version

from lymph.core.versioning import parse_versioned_name, compatible

from lymph.schema import message


class Schema(object):
    def __init__(self, raw):
        self.__raw = raw

    @property
    def services(self):
        return self.__raw.keys()

    def build_service(self, name):
        name, version = parse_versioned_name(name)
        if version:
            version = self._get_best_match(name, version)
        version = str(version) if version else ''

        try:
            methods = self.__raw[name][version]['methods']
        except KeyError:
            raise ValueError("unknown service or version")
        return Service(name, version, methods)

    def todict(self):
        return self.__raw

    def _get_best_match(self, name, version):
        spec = compatible(version)
        return spec.select(Version(v) for v in self.__raw[name])


class Service(message.BuilderMixin):
    """A hermetic service emulating a remote lymph interface."""
    def __init__(self, name, version, methods):
        super(Service, self).__init__()
        self.__name = name
        self.__version = version
        self.__methods = methods

    @property
    def methods(self):
        return self.__methods

    @property
    def name(self):
        return self.__name

    @property
    def versionned_name(self):
        if self.__version:
            return '%s@%s' % (self.__name, self.__version)
        return self.__name

    @property
    def schema(self):
        return {
            self.__name: {
                self.__version: {
                    'methods': self.__methods,
                }
            }
        }

    def __getattr__(self, meth):
        if meth not in self.__methods:
            raise AttributeError("unknown attribute %s" % meth)
        return self._get_method(meth)

    def _get_method(self, meth):
        acc_args = self.__methods[meth]['args']
        acc_kwargs = self.__methods[meth]['kwargs']

        def _inner(**kwargs):
            self._validate_args(meth, kwargs, acc_args, acc_kwargs)

            return self._get_message(meth, self.__methods[meth]['returns'])
        return _inner

    @staticmethod
    def _validate_args(func_name, passed_kwargs, acc_args, acc_kwargs):
        for a in passed_kwargs:
            if not (a in acc_kwargs or a in acc_args):
                raise TypeError('%s() got an unexpected keyword argument %r' % (func_name, a))

        for a in acc_args:
            if a not in passed_kwargs:
                raise TypeError('%s() takes exactly %d argument (%d given)' % (func_name, (len(acc_args)), len(passed_kwargs)))


