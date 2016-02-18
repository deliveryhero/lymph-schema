import abc

import mock
import six
from lymph.testing import RpcMockTestCase
from lymph.exceptions import Nack

from lymph.schema import message


# TODO: assert_called_n
# TODO: assert_called_once
@six.add_metaclass(abc.ABCMeta)
class MockServiceTester(RpcMockTestCase):

    @abc.abstractproperty
    def rpc_schema(self):
        pass

    def setUp(self):
        super(MockServiceTester, self).setUp()
        self.mocker = Mocker(self)

    # XXX: Arguments name are prefixed with '__' to not collide with **kwargs keys.
    def assert_called(self, __name, __meth, **kwargs):
        name = '%s.%s' % (__name, __meth)
        self.assert_any_rpc_calls(mock.call(name, **kwargs))

    def assert_not_called(self, __name, __meth, **kwargs):
        try:
            self.assert_called(__name, __meth, **kwargs)
        except AssertionError:
            pass
        else:
            call = _format_call(__name, __meth, kwargs)
            raise AssertionError("%s called, expected to not be called" % call)


class Mocker(object):
    def __init__(self, testcase):
        self._testcase = testcase
        self._services = {}

    def on(self, name, meth, **kwargs):
        svc = self._get_service(name)
        return MockCall(self._testcase, svc, meth)

    def _get_service(self, name):
        try:
            svc = self._services[name]
        except KeyError:
            svc = self._testcase.rpc_schema.build_service(name)
            self._services[name] = svc

            mocks = {}
            for m in svc.methods:
                mocks['%s.%s' % (svc.name, m)] = getattr(svc, m)

            self._testcase.setup_rpc_mocks(mocks)

        return svc


class MockCall(object):
    def __init__(self, testcase, service, meth):
        self._testcase = testcase
        self._meth = meth
        self._service = service

    def raises(self, exc):
        name = '%s.%s' % (self._service.name, self._meth)
        allowed_excs = self._service.methods[self._meth]['raises']
        if not (isinstance(exc, Nack) or exc.__class__.__name__ in allowed_excs):
            raise ValueError(
                '%s cannot raise %s, only can raise one of this exceptions: %s'
                % (name, exc.__class__, allowed_excs))
        self._testcase.update_rpc_mock(name, exc)

    def returns(self, ret):
        # TODO: Check if type matches with what is expected to be returned.
        if isinstance(ret, dict):
            msg = message.build(
                self._service.schema,
                self._service.versionned_name,
                self._meth)
            msg.update(ret)
            ret = msg
        self._service.set_message(self._meth, ret)


def _format_call(name, meth, kwargs):
    """Format a call to pretty presentation

    Example:

        >>> _format_call('users@1.10.1', 'change', pwd="123abcd")
        '<users@1.10.1>.change(pwd="123abc")'

    """
    f_kwargs = ', '.join("%s=%r" % (k, v) for k, v in kwargs.items())
    return "<%s>.%s(%s)" (name, meth, f_kwargs)
