"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries

# Third Party Libraries
from loguru import logger

# Local Libraries
import eaip_parser
from . import validate, webscrape

@logger.catch
def main() -> None:
    """Main program thread"""

    logger.info(f"eAIP Parser and Sector File Validator - v{eaip_parser.__version__}")

    # Run the webscraper
    scrape = webscrape.Webscrape()
    scrape.run()

    # Run the validator
    validator = validate.UkSectorFile()
    validator.airways_rnav()
    validator.vor_dme_tacan()

if __name__ == "__main__":
    main()
