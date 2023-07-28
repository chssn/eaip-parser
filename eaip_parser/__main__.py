"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries

# Third Party Libraries
from loguru import logger

# Local Libraries
from . import webscrape

@logger.catch
def main() -> None:
    """Main program thread"""

    # Run the webscraper
    scrape = webscrape.Webscrape()
    scrape.run()

if __name__ == "__main__":
    main()
