from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.resolve()))
import reposter.autotests.run
import reposter.funcs.other
import reposter.core.common
import reposter.core.config
import reposter.core.types
import asyncio


async def main():
    await reposter.funcs.other.init()
    with reposter.core.types.Progress(
        console=reposter.core.common.app.console
    ) as progress:
        reposter.core.common.app.progress = progress
        if reposter.core.config.env.tests or reposter.core.config.env.big_tests:
            await reposter.autotests.run.main()
        else:
            print('running app')


if __name__ == '__main__':
    asyncio.run(main())

