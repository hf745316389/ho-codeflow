"""Publish a report to the company-wide #analytics channel.

Everyone in the workspace sees the message immediately. Posts cannot be
recalled.

Usage: python scripts/publish_report.py <report.json>
"""

import os
import sys

WEBHOOK_ENV = "ANALYTICS_WEBHOOK_URL"


def main():
    if len(sys.argv) < 2:
        print("usage: publish_report.py <report.json>")
        return 1
    url = os.environ.get(WEBHOOK_ENV)
    if not url:
        print("error: %s is not set" % WEBHOOK_ENV)
        return 1
    # Real implementation POSTs sys.argv[1] to `url`.
    print("posted %s to %s" % (sys.argv[1], url))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
