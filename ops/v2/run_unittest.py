"""Run real unittest discovery, record counts, and fail on zero tests or SKIP."""
import argparse
import json
from pathlib import Path
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    parser.add_argument('pattern')
    parser.add_argument('result', type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(args.directory, pattern=args.pattern)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    counts = {'tests': result.testsRun, 'fail': len(result.failures),
              'error': len(result.errors), 'skip': len(result.skipped),
              'expected_failure': len(result.expectedFailures),
              'unexpected_success': len(result.unexpectedSuccesses)}
    counts['pass'] = (counts['tests'] - sum(counts[k] for k in
                      ('fail', 'error', 'skip', 'expected_failure', 'unexpected_success')))
    args.result.write_text(json.dumps(counts, indent=2) + '\n')
    print(json.dumps(counts))
    return int(not result.wasSuccessful() or counts['tests'] == 0 or
               counts['skip'] > 0 or counts['expected_failure'] > 0)


if __name__ == '__main__':
    raise SystemExit(main())
