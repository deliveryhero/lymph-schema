import unittest

from lymph.schema import fake


class StubTest(unittest.TestCase):

    schema = {
        'users': {
            '0.1.0': {
                'methods': {
                    'get': {
                        'args': ['id'],
                        'kwargs': {'name': None},
                        'doc': '',
                        'raises': [],
                        'name': 'get',
                        'returns': {'type': 'integer'},
                    },
                },
            },
        },
    }

    def test_build(self):
        users = fake.build(self.schema, 'users@0.1.0')

        with self.assertRaises(AttributeError):
            users.unknown()

        with self.assertRaises(TypeError):
            users.get()

        users.get(id=1)

        users.get(id=1, name='string')

    def test_build_unknown_service(self):
        with self.assertRaises(ValueError):
            fake.build(self.schema, 'unknown')

        with self.assertRaises(ValueError):
            fake.build(self.schema, 'users@11.0.4')
