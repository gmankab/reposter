import sys
import rich.traceback
rich.traceback.install()

if '-m' not in sys.argv:
    try:
        import main
    except ImportError as error1:
        try:
            from reposter import main
        except ImportError as error2:
            raise error1 from error2
