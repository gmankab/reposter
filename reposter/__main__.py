import sys
import rich
rich.traceback.install()

if '-m' not in sys.argv:
    try:
        import main
    except ImportError:
        from reposter import main
