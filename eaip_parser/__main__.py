"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import sys

# Third Party Libraries
from loguru import logger

# Local Libraries
import eaip_parser
from . import compare, webscrape

@logger.catch
def main() -> None:
    """Main program thread"""

    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.info(f"eAIP Parser and Sector File Validator - {eaip_parser.__version__}")

    # Run the webscraper
    scrape = webscrape.Webscrape()
    scrape.run()

    # Run the comparison
    comp = compare.UkSectorFile()
    comp.airways_rnav()
    comp.vor_dme_tacan()

if __name__ == "__main__":
    main()
