import sys
try:
    from pp.pkglib.multipkg import setup
except ImportError:
    print "pp-pkglib is missing, please update your environment"
    sys.exit(1)

setup()
