from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.resolve()))
import reposter.funcs.status
import reposter.funcs.other
import reposter.core.common
import reposter.core.config
import reposter.core.types
import reposter.tg.handlers
import asyncio


async def main():
    await reposter.funcs.other.init()
    reposter.core.common.log(
        reposter.funcs.status.status.get()
    )
    with reposter.core.types.Progress(
        console=reposter.core.common.app.console
    ) as progress:
        reposter.core.common.app.progress = progress
        if reposter.core.config.env.tests or reposter.core.config.env.big_tests:
            import reposter.autotests.run as tests
            await tests.main()
        else:
            await reposter.tg.handlers.main()


if __name__ == '__main__':
    asyncio.run(main())

