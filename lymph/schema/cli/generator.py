import json

from lymph.cli.base import Command

from lymph.schema import generator as gen


class SchemaGenerator(Command):
    """
    Usage: lymph gen-schema <config> [options]

    Generate rpc schema from service configuration.

    {COMMON_OPTIONS}

    """

    needs_config = False
    short_description = 'Generate schema from service configuration'

    def run(self):
        config_file = self.args['<config>']

        schema = gen.generate_from_config(config_file)
        print json.dumps(schema.todict(), indent=4)

