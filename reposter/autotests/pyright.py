import reposter.core.common
import reposter.core.types
import platform
import asyncio
import sys


async def pyright() -> str:
    pyrightconfig = reposter.core.common.path.pyproject_toml
    python_version = platform.python_version()
    cmd = [
        sys.executable,
        '-m',
        'pyright',
        str(reposter.core.common.path.app_dir),
        f'--project={pyrightconfig}',
        f'--pythonpath={sys.executable}',
        f'--pythonversion={python_version}',
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
    success = '0 errors, 0 warnings, 0 information'
    if success in stdout_str.lower():
        return f'pyright: {stdout_str}'
    else:
        raise reposter.core.types.NotPassedError(stdout_str + stderr_str)

