import sys

if '-m' not in sys.argv:
    try:
        from reposter import main
    except ImportError:
        import main
