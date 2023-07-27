"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# A list of country codes and associated language
country_codes = {
    "EG": "en-GB",
}

# A list of sections contained in the eAIP excluding aerodrome specific pages
eaip_sections = [
    "ENR-1.6",
    "ENR-1.8",
    "ENR-2.1",
    "ENR-2.2",
    "ENR-3.1",
    "ENR-3.2",
    "ENR-3.3",
    "ENR-3.4",
    "ENR-4.1",
    "ENR-4.2",
    "ENR-4.4",
    "ENR-5.1",
    "ENR-5.2",
    "ENR-5.3",
    "ENR-5.4",
    "ENR-5.5",
    "ENR-5.6",
    "AD-1.3",
]