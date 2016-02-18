import uuid

import lymph

from lymph.schema.decorator import spec


class NotFound(Exception):
    pass


class Users(lymph.Interface):
    @lymph.rpc(raises=NotFound)
    @spec(returns=dict)
    def get(self, id):
        pass

    @lymph.rpc()
    @spec(returns=uuid.UUID)
    def register(self, values):
        pass


class Echo(lymph.Interface):
    @lymph.rpc()
    @spec(returns=str)
    def ping(self, text=''):
        return text
