import reposter.core.common
import tortoise


async def init():
    await tortoise.Tortoise.init(
        db_url=reposter.core.common.app.db_url,
        modules={'models': ['reposter.db.models']}
    )
    await tortoise.Tortoise.generate_schemas()

