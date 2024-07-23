import reposter.core.common
from tortoise.models import Model
from tortoise import fields


class Msg(Model):
    src_msg = fields.IntField()
    src_chat = fields.IntField()
    target_msg = fields.IntField()
    target_chat = fields.IntField()


async def create():
    await Msg.create(
        src_msg=1,
        src_chat=2,
        target_msg=3,
        target_chat=4,
    )
    reposter.core.common.log(
        await Msg.all().first().values()
    )
    import os
    os._exit(0)

