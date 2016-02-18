import os
import tempfile
import unittest

import mock

import lymph
from lymph.schema import generator as gen


CONFIG = """
interfaces:
    dummy@0.1.0:
        class: lymph.schema.tests.generator_test:Dummy
    dummy@1.0.2:
        class: lymph.schema.tests.generator_test:DummyV1
"""


class Dummy(lymph.Interface):
    @lymph.rpc(raises=ValueError)
    def rpc_method(self, values, foo=None):
        'a dummy rpc function'
        return

    @lymph.raw_rpc()
    def raw_rpc_method(self, values):
        return

    def normal_method(self, id):
        pass


class DummyV1(lymph.Interface):
    @lymph.rpc(raises=(TypeError, ValueError))
    def another_rpc_method(self, values):
        return


class GeneratorTestCase(unittest.TestCase):

    maxDiff = None

    def test_rpc_spec(self):
        spec = gen._get_rpc_spec(Dummy.rpc_method)

        self.assertEqual(spec.name, 'rpc_method')
        self.assertEqual(spec.args, ['values'])
        self.assertEqual(spec.kwargs, {'foo': None})
        self.assertEqual(spec.doc, 'a dummy rpc function')
        self.assertEqual(spec.raises, ['ValueError'])
        self.assertEqual(spec.returns, {})

    def test_rpc_methods(self):
        methods = gen._get_rpc_methods(Dummy)

        self.assertEqual(len(methods), 2)
        self.assertDictEqual(methods['rpc_method'], {
            'name': 'rpc_method',
            'args': ['values'],
            'kwargs': {'foo': None},
            'doc': 'a dummy rpc function',
            'raises': ['ValueError'],
            'returns': {},
        })
        self.assertDictEqual(methods['raw_rpc_method'], {
            'name': 'raw_rpc_method',
            'args': ['values'],
            'kwargs': {},
            'doc': '',
            'raises': [],
            'returns': {},
        })

    def test_generate_from_interface(self):
        schema = gen.generate_from_interface(Dummy(mock.MagicMock(), 'dummy', version='0.1.0', builtin=True))

        self.assertEqual(schema.todict(), {
            'dummy': {
                '0.1.0': {
                    'methods': {
                        'rpc_method': {
                            'name': 'rpc_method',
                            'args': ['values'],
                            'kwargs': {'foo': None},
                            'doc': 'a dummy rpc function',
                            'raises': ['ValueError'],
                            'returns': {},
                        },
                        'raw_rpc_method': {
                            'name': 'raw_rpc_method',
                            'args': ['values'],
                            'kwargs': {},
                            'doc': '',
                            'raises': [],
                            'returns': {},
                        },
                    },
                },
            }
        })

    def test_generate_from_config(self):
        fd, filepath = tempfile.mkstemp()
        os.close(fd)

        with open(filepath, 'w') as f:
            f.write(CONFIG)

        schema = gen.generate_from_config(filepath)

        self.assertEqual(schema.todict(), {
            'dummy': {
                '0.1.0': {
                    'methods': {
                        'rpc_method': {
                            'name': 'rpc_method',
                            'args': ['values'],
                            'kwargs': {'foo': None},
                            'doc': 'a dummy rpc function',
                            'raises': ['ValueError'],
                            'returns': {},
                        },
                        'raw_rpc_method': {
                            'name': 'raw_rpc_method',
                            'args': ['values'],
                            'kwargs': {},
                            'doc': '',
                            'raises': [],
                            'returns': {},
                        },
                    },
                },
                '1.0.2': {
                    'methods': {
                        'another_rpc_method': {
                            'name': 'another_rpc_method',
                            'args': ['values'],
                            'kwargs': {},
                            'doc': '',
                            'raises': ['TypeError', 'ValueError'],
                            'returns': {},
                        },
                    },
                },
            }
        })
