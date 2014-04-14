import sys
try:
    from pkglib.multipkg import setup
except ImportError:
    print "pkglib is missing, please update your environment"
    sys.exit(1)

setup()
