import inspect
import sys
import unittest
from importlib import import_module

from . import DOMAINS, catalog, n_checks, _public


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(__doc__ or "usage: python3 -m pfv list [domain] | doc <name> | selftest")
        import pfv
        print(pfv.__doc__)
        return 0
    cmd = argv[1]
    if cmd == "list":
        print(catalog(argv[2] if len(argv) > 2 else None))
        print(f"\n{n_checks()} check_/hunt_ functions across {len(DOMAINS)} domains")
        return 0
    if cmd == "doc":
        name = argv[2]
        for d in DOMAINS:
            mod = import_module(f".{d}", "pfv")
            for n, f in _public(mod):
                if n == name:
                    print(f"pfv.{d}.{n}{inspect.signature(f)}\n")
                    print(inspect.getdoc(f) or "(no docstring)")
                    return 0
        print("no such check", file=sys.stderr)
        return 1
    if cmd == "selftest":
        import os
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        suite = unittest.defaultTestLoader.discover(os.path.join(here, "tests"), pattern="test_*.py", top_level_dir=here)
        res = unittest.TextTestRunner(verbosity=1).run(suite)
        return 0 if res.wasSuccessful() else 1
    print("unknown command", cmd, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
