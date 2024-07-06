import reposter.core.common
import platform
import subprocess
import datetime
import shutil


class Status:
    def __init__(self) -> None:
        self.start_time = datetime.datetime.now()

    def get(self) -> dict[str, str]:
        bot = reposter.core.common.tg.client.me
        assert bot
        return {
            'config_path': str(reposter.core.common.path.config_json),
            'app_version': reposter.core.common.app.version,
            'app_uptime': self.get_app_uptime(),
            'system': self.get_system_name(),
            'system_uptime': self.get_system_uptime(),
            'kernel': platform.release(),
            'python_ver:': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'commit': self.get_commit_hash(),
            'username': bot.username,
            'name': bot.full_name,
            'id': str(bot.id),
        }

    def get_system_name(self) -> str:
        system_name: str = platform.system()
        if system_name == 'Linux':
            try:
                return platform.freedesktop_os_release()['PRETTY_NAME']
            except Exception:
                pass
        return system_name

    def get_app_uptime(self) -> str:
        backend_uptime = datetime.datetime.now() - self.start_time
        days = backend_uptime.days
        seconds = backend_uptime.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{days} days, {hours} hours, {minutes} minutes"

    def get_system_uptime(self) -> str:
        try:
            uptime = subprocess.run(
                ['uptime'],
                text=True,
                capture_output=True,
            )
        except Exception:
            return ''
        else:
            return uptime.stdout.strip()

    def get_commit_hash(self) -> str:
        git = shutil.which('git')
        if not git:
            return ''
        result = subprocess.run(
            [git, 'rev-parse', '--short', 'HEAD'],
            cwd=reposter.core.common.path.app_dir,
            capture_output=True,
            check=False,
            text=True,
        )
        return result.stdout.strip()


status = Status()

