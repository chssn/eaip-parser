"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.9

# Standard Libraries
import sys

# Third Party Libraries
from loguru import logger

# Local Libraries
import eaip_parser
from eaip_parser import compare, webscrape

@logger.catch
def main() -> None:
    """Main program thread"""

    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.info(f"eAIP Parser and Sector File Validator - {eaip_parser.__VERSION__}")

    # Run the webscraper
    scrape = webscrape.Webscrape()
    scrape.run()

    # Run the comparison
    comp = compare.UkSectorFile()
    comp.airways_rnav()
    comp.vor_dme_tacan()

if __name__ == "__main__":
    main()
