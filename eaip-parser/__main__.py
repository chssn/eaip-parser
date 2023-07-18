"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries

# Third Party Libraries

# Local Libraries
from . import webscrape

run_it = webscrape.Webscrape()
#run_it.parse_ad_01_data()
run_it.run()
