import json
import os
import tempfile

from lymph.cli.testing import CliIntegrationTestCase


CONFIG = """
interfaces:
    users@0.5.1:
       class: lymph.schema.tests.interfaces:Users
    echo:
       class: lymph.schema.tests.interfaces:Echo
"""


class GenSchemaCliTest(CliIntegrationTestCase):

    maxDiff = None

    def setUp(self):
        super(GenSchemaCliTest, self).setUp()
        fp, self.config_file = tempfile.mkstemp()
        os.close(fp)
        with open(self.config_file, 'w') as f:
            f.write(CONFIG)

    def test_schema_generate(self):
        res = self.cli(['gen-schema', self.config_file])

        self.assertEqual(res.returncode, 0)

        stdout = json.loads(res.stdout)

        self.assertEqual(stdout, {
            'users': {
                '0.5.1': {
                    'methods': {
                        'get': {
                            'args': ['id'],
                            'kwargs': {},
                            'raises': ['NotFound'],
                            'doc': '',
                            'returns': {'type': 'object'},
                            'name': 'get',
                        },
                        'register': {
                            'args': ['values'],
                            'kwargs': {},
                            'raises': [],
                            'doc': '',
                            'name': 'register',
                            'returns': {'type': 'string', 'format': 'uuid'},
                        },
                    },
                },
            },
            'echo': {
                '': {
                    'methods': {
                        'ping': {
                            'args': [],
                            'kwargs': {'text': ''},
                            'raises': [],
                            'doc': '',
                            'name': 'ping',
                            'returns': {'type': 'string'},
                        }
                    },
                },
            },
        })
