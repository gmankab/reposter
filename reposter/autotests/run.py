from reposter.core.common import log
from reposter.autotests import restricted
import reposter.funcs.other


async def main():
    to_run = [
        # repost.unrestricted,
        # restricted.big_document,
        restricted.restricted,
    ]
    for func in to_run:
        msg = await func()
        log(msg)
    await reposter.funcs.other.shutdown()

