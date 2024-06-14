import reposter.core.common
import reposter.core.types
import asyncio
import sys


async def ruff() -> str:
    cmd = [
        sys.executable,
        '-m',
        'ruff',
        'check',
        str(reposter.core.common.path.app_dir),
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stdout_str = stdout.decode().strip()
    stderr_str = stderr.decode().strip()
    success = 'all checks passed'
    if success in stdout_str.lower():
        return f'ruff: {stdout_str}'
    else:
        raise reposter.core.types.NotPassedError(stdout_str + stderr_str)

