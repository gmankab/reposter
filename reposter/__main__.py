from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.resolve()))
from reposter.core.config import env
import reposter.handlers.set
import reposter.funcs.status
import reposter.funcs.other
import reposter.core.common
import reposter.core.types
import asyncio


async def async_main():
    await reposter.funcs.other.init()
    reposter.core.common.log(
        reposter.funcs.status.status.get()
    )
    with reposter.core.types.Progress(
        console=reposter.core.common.app.console
    ) as progress:
        reposter.core.common.app.progress = progress
        if env.source or env.target or env.msg_start or env.msg_stop:
            import reposter.shortshot.shortshot as shortshot
            await shortshot.main()
            await reposter.funcs.other.shutdown()
            return
        if env.tests or env.big_tests:
            import reposter.autotests.run as tests
            await tests.main()
            await reposter.funcs.other.shutdown()
        await reposter.handlers.set.main()


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()

