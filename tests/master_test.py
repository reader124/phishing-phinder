"""Run the complete test suite and print a summary."""

import sys
import unittest
import importlib.util
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent


def run_all_tests() -> int:
    """Discover and run every test module in the tests directory."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Load test files directly so ``tests`` does not need an __init__.py.
    for test_file in sorted(TESTS_DIR.glob("test_*.py")):
        if test_file.name == Path(__file__).name:
            continue

        module_name = f"master_suite_{test_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load test file: {test_file}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        suite.addTests(loader.loadTestsFromModule(module))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    failed = len(result.failures) + len(result.errors)
    skipped = len(result.skipped)
    passed = result.testsRun - failed - skipped

    print("\nTest summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if skipped:
        print(f"Skipped: {skipped}")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(run_all_tests())
