#!/usr/bin/env python3
"""Post-render: drop unlisted pages from sitemap.xml.

Quarto's `search: false` keeps a page out of the site search index but still
lists it in sitemap.xml. Anything named here is stripped after every render so
the page stays reachable by URL without being advertised to crawlers.
"""

import os
import re
import sys

UNLISTED = ["demo_script.html"]


def main() -> int:
    output_dir = os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site.nosync")
    sitemap = os.path.join(output_dir, "sitemap.xml")
    if not os.path.exists(sitemap):
        return 0

    with open(sitemap, encoding="utf-8") as fh:
        xml = fh.read()

    for page in UNLISTED:
        pattern = r"\s*<url>(?:(?!</url>).)*?" + re.escape(page) + r"(?:(?!</url>).)*?</url>"
        xml, n = re.subn(pattern, "", xml, flags=re.DOTALL)
        if n:
            print(f"[exclude-from-sitemap] removed {page} from sitemap.xml")

    with open(sitemap, "w", encoding="utf-8") as fh:
        fh.write(xml)
    return 0


if __name__ == "__main__":
    sys.exit(main())
