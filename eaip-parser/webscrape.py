"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import math
import re
import warnings

# Third Party Libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

# Local Libraries
from . import airac, functions

warnings.filterwarnings("ignore", category=UserWarning)

class Webscrape:
    """Class to scrape data from the given AIRAC eAIP URL"""

    def __init__(self, next_cycle:bool=False, country_code:str="EG"):
        airac_cycle = airac.Airac()
        self.cycle = airac_cycle.cycle(next_cycle=next_cycle)
        self.cycle_url = airac_cycle.url(next_cycle=next_cycle)
        self.country = country_code

    def get_table_soup(self, post_url:str) -> BeautifulSoup:
        """Parse the given table into a beautifulsoup object"""

        address = self.cycle_url + post_url
        logger.debug(address)

        try:
            response = requests.get(address)
        except requests.ConnectionError as err:
            logger.exception(f"Unable to connect to {address} with error {err}")

        if response.status_code != 200:
            logger.error(f"Unable to connect to {address} with status code {response.status_code}")
            return False
        return BeautifulSoup(response.content, "lxml")

    def parse_ad_01_data(self) -> pd.DataFrame:
        """Parse the data from AD-0.1"""

        logger.info("Parsing "+ self.country +"-AD-0.1 data to obtain ICAO designators...")

        # create the table
        df_columns = [
            'icao_designator',
            'verified',
            'location',
            'elevation',
            'name',
            'magnetic_variation'
            ]
        df_store = pd.DataFrame(columns=df_columns)

        # scrape the data
        get_aerodrome_list = self.get_table_soup(self.country + "-AD-0.1-en-GB.html")

        # process the data
        list_aerodrome_list = get_aerodrome_list.find_all("h3")
        for row in list_aerodrome_list:
            # search for aerodrome icao designator and name
            get_aerodrome = re.search(rf"({self.country}[A-Z]{{2}})(\n[\s\S]{{7}}\n[\s\S]{{8}})([A-Z]{{4}}.*)(\n[\s\S]{{6}}<\/a>)", str(row))
            if get_aerodrome:
                # Place each aerodrome into the DB
                df_out = pd.DataFrame({
                    'icao_designator': str(get_aerodrome[1]),
                    'verified': 0,
                    'location': 0,
                    'elevation': 0,
                    'name': str(get_aerodrome[3]),
                    'magnetic_variation': 0
                    }, index=[0])
                df_store = pd.concat([df_store, df_out], ignore_index=True)

        return df_store

    def parse_ad_02_data(self, df_ad_01:pd.DataFrame) -> list:
        """Parse the data from AD-2.x"""

        logger.info("Parsing "+ self.country +"-AD-2.x data to obtain aerodrome data...")
        df_columns_rwy = ['icao_designator','runway','location','elevation','bearing','length']
        df_rwy = pd.DataFrame(columns=df_columns_rwy)

        df_columns_srv = ['icao_designator','callsign_type','frequency']
        df_srv = pd.DataFrame(columns=df_columns_srv)

        # Select all aerodromes in the database
        for index, row in df_ad_01.iterrows():
            aero_icao = row['icao_designator']
            # Select all runways in this aerodrome
            get_runways = self.get_table_soup(self.country + "-AD-2."+ aero_icao +"-en-GB.html")
            if get_runways:
                logger.info("Parsing AD-2 data for " + aero_icao)
                aerodrome_ad_02_02 = get_runways.find(id=aero_icao + "-AD-2.2")
                aerodrome_ad_02_12 = get_runways.find(id=aero_icao + "-AD-2.12")
                aerodrome_ad_02_18 = get_runways.find(id=aero_icao + "-AD-2.18")

                # Find current magnetic variation for this aerodrome
                aerodrome_mag_var = self.search("([\d]{1}\.[\d]{2}).([W|E]{1})", "TAD_HP;VAL_MAG_VAR", str(aerodrome_ad_02_02))
                plus_minus = functions.Geo.plus_minus(aerodrome_mag_var[0][1])
                float_mag_var = plus_minus + aerodrome_mag_var[0][0]

                # Find lat/lon/elev for aerodrome
                aerodrome_lat = re.search(r'(Lat: )(<span class="SD" id="ID_[\d]{7,}">)([\d]{6})([N|S]{1})', str(aerodrome_ad_02_02))
                aerodrome_lon = re.search(r"(Long: )(<span class=\"SD\" id=\"ID_[\d]{7,}\">)([\d]{7})([E|W]{1})", str(aerodrome_ad_02_02))
                aerodrome_elev = re.search(r"(VAL_ELEV\;)([\d]{1,4})", str(aerodrome_ad_02_02))

                logger.trace(aerodrome_lat)
                logger.trace(aerodrome_lon)

                try:
                    full_location = self.sct_location_builder(
                        aerodrome_lat.group(3),
                        aerodrome_lon.group(3),
                        aerodrome_lat.group(4),
                        aerodrome_lon.group(4)
                        )
                except AttributeError as err:
                    logger.warning(err)
                    continue

                df_ad_01.at[index, 'verified'] = 1
                df_ad_01.at[index, 'magnetic_variation'] = str(float_mag_var)
                df_ad_01.at[index, 'location'] = str(full_location)
                df_ad_01.at[index, 'elevation'] = str(aerodrome_elev[2])

                # Find runway locations
                aerodrome_runways = self.search("([\d]{2}[L|C|R]?)", "TRWY_DIRECTION;TXT_DESIG", str(aerodrome_ad_02_12))
                aerodrome_runways_lat = self.search("([\d]{6}\.[\d]{2}[N|S]{1})", "TRWY_CLINE_POINT;GEO_LAT", str(aerodrome_ad_02_12))
                aerodrome_runways_long = self.search("([\d]{7}\.[\d]{2}[E|W]{1})", "TRWY_CLINE_POINT;GEO_LONG", str(aerodrome_ad_02_12))
                aerodrome_runways_elev = self.search("([\d]{3}\.[\d]{1})", "TRWY_CLINE_POINT;VAL_ELEV", str(aerodrome_ad_02_12))
                aerodrome_runways_bearing = self.search("([\d]{3}\.[\d]{2}.)", "TRWY_DIRECTION;VAL_TRUE_BRG", str(aerodrome_ad_02_12))
                aerodrome_runways_len = self.search("([\d]{3,4})", "TRWY;VAL_LEN", str(aerodrome_ad_02_12))

                for rwy, lat, lon, elev, brg, rwy_len in zip(aerodrome_runways, aerodrome_runways_lat, aerodrome_runways_long, aerodrome_runways_elev, aerodrome_runways_bearing, aerodrome_runways_len):
                    # Add runway to the aerodromeDB
                    lat_split = re.search(r"([\d]{6}\.[\d]{2})([N|S]{1})", str(lat))
                    lon_split = re.search(r"([\d]{7}\.[\d]{2})([E|W]{1})", str(lon))

                    loc = self.sct_location_builder(
                        lat_split.group(1),
                        lon_split.group(1),
                        lat_split.group(2),
                        lon_split.group(2)
                        )

                    df_rwy_out = pd.DataFrame({
                        'icao_designator': str(aero_icao),
                        'runway': str(rwy),
                        'location': str(loc),
                        'elevation': str(elev),
                        'bearing': str(brg.rstrip('°')),
                        'length': str(rwy_len)
                        }, index=[0])
                    df_rwy = pd.concat([df_rwy, df_rwy_out], ignore_index=True)

                # Find air traffic services
                aerodrome_services = self.search("(APPROACH|GROUND|DELIVERY|TOWER|DIRECTOR|INFORMATION|RADAR|RADIO|FIRE|EMERGENCY)", "TCALLSIGN_DETAIL", str(aerodrome_ad_02_18))
                service_frequency = self.search("([\d]{3}\.[\d]{3})", "TFREQUENCY", str(aerodrome_ad_02_18))

                last_srv = ''
                if len(aerodrome_services) == len(service_frequency):
                    # Simple aerodrome setups with 1 job, 1 frequency
                    for srv, frq in zip(aerodrome_services, service_frequency):
                        if str(srv) is None:
                            s_type = last_srv
                        else:
                            s_type = str(srv)
                            last_srv = s_type
                        df_srv_out = pd.DataFrame({'icao_designator': str(aero_icao),'callsign_type': s_type,'frequency': str(frq)}, index=[0])
                        df_srv = pd.concat([df_srv, df_srv_out], ignore_index=True)
                else:
                    # Complex aerodrome setups with multiple frequencies for the same job
                    logger.warning(f"Aerodrome {aero_icao} has a complex comms structure!")
                    for row in aerodrome_ad_02_18.find_all("span"):
                        # get the full row and search between two "TCALLSIGN_DETAIL" objects
                        table_row = re.search(r"(APPROACH|GROUND|DELIVERY|TOWER|DIRECTOR|INFORMATION|RADAR|RADIO|FIRE|EMERGENCY)", str(row))
                        if table_row is not None:
                            callsign_type = table_row.group(1)
                        freq_row = re.search(r"([\d]{3}\.[\d]{3})", str(row))
                        if freq_row is not None:
                            frequency = str(freq_row.group(1))
                            if frequency != "121.500": # filter out guard frequencies
                                df_srv_out = pd.DataFrame({'icao_designator': str(aero_icao),'callsign_type': callsign_type,'frequency': frequency}, index=[0])
                                df_srv = pd.concat([df_srv, df_srv_out], ignore_index=True)
            else:
                logger.error(f"Aerodrome {aero_icao} does not exist")

        return [df_ad_01, df_rwy, df_srv]

    def parse_enr_016_data(self, df_ad_01:pd.DataFrame) -> pd.DataFrame:
        """Parse the data from ENR-1.6"""

        logger.info("Parsing "+ self.country + "-ENR-1.6 data to obtan SSR code allocation plan")
        df_columns = ['start','end','depart','arrive', 'string']
        df_store = pd.DataFrame(columns=df_columns)

        webpage = self.get_table_soup(self.country + "-ENR-1.6-en-GB.html")
        get_div = webpage.find("div", id = "ENR-1.6.2.6")
        get_tr = get_div.find_all('tr')
        for row in get_tr:
            get_p = row.find_all('p')
            if len(get_p) > 1:
                # this will just return ranges and ignore all discreet codes in the table
                text = re.search(r"([\d]{4})...([\d]{4})", get_p[0].text)
                if text:
                    start = text.group(1)
                    end = text.group(2)

                    # create an array of words to search through to try and match code range to destination airport
                    loc_array = get_p[1].text.split()
                    for loc in loc_array:
                        strip = re.search(r"([A-Za-z]{3,10})", loc)
                        if strip:
                            dep = self.country + "\w{2}"
                            # search the dataframe containing icao_codes
                            name = df_ad_01[df_ad_01['name'].str.contains(strip.group(1), case=False, na=False)]
                            if len(name.index) == 1:
                                df_out = pd.DataFrame({'start': start,'end': end,'depart': dep,'arrive': name.iloc[0]['icao_designator'],'string': strip.group(1)}, index=[0])
                                df_store = pd.concat([df_store, df_out], ignore_index=True)
                            elif strip.group(1) == "RAF" or strip.group(1) == "Military" or strip.group(1) == "RNAS" or strip.group(1) == "NATO":
                                df_out = pd.DataFrame({'start': start,'end': end,'depart': dep,'arrive': 'Military','string': strip.group(1)}, index=[0])
                                df_store = pd.concat([df_store, df_out], ignore_index=True)
                            elif strip.group(1) == "Transit":
                                df_out = pd.DataFrame({'start': start,'end': end,'depart': dep,'arrive': loc_array[2],'string': strip.group(1)}, index=[0])
                                df_store = pd.concat([df_store, df_out], ignore_index=True)

        return df_store

    def parse_enr_02_data(self) -> list:
        """Parse the data from ENR-2"""

        df_columns = ['name', 'callsign', 'frequency', 'boundary', 'upper_fl', 'lower_fl']
        df_fir = pd.DataFrame(columns=df_columns)
        df_uir = pd.DataFrame(columns=df_columns)
        df_cta = pd.DataFrame(columns=df_columns)
        df_tma = pd.DataFrame(columns=df_columns)

        logger.info("Parsing "+ self.country +"-ENR-2.1 Data (FIR, UIR, TMA AND CTA)...")
        get_data = self.get_table_soup(self.country + "-ENR-2.1-en-GB.html")

        # create a list of complex airspace areas with the direction of the arc for reference later on
        df_columns = ['area', 'number', 'direction']
        complex_areas = pd.DataFrame(columns=df_columns)
        row = 0
        complex_search_data = get_data.find_all("p") # find everything enclosed in <p></p> tags
        complex_len = len(complex_search_data)
        while row < complex_len:
            title = re.search(r"id=\"ID_[\d]{8,10}\"\>([A-Z]*)\s(FIR|CTA|TMA|CTR)\s([0-9]{0,2})\<", str(complex_search_data[row]))
            if title:
                print_title = f"{str(title.group(1))} {str(title.group(2))} {str(title.group(3))}"

                direction = re.findall(r"(?<=\s)(anti-clockwise|clockwise)(?=\s)", str(complex_search_data[row+1]))
                if direction:
                    area_number = 0
                    for dtn in direction:
                        ca_out = pd.DataFrame({'area': print_title, 'number': str(area_number), 'direction': str(dtn)}, index=[0])
                        complex_areas = pd.concat([complex_areas, ca_out], ignore_index=True)
                        area_number += 1
                    row += 1
            row += 1
        complex_areas.to_csv(f'{functions.work_dir}\\DataFrames\enr_02-CW-ACW-Helper.csv')

        search_data = get_data.find_all("span")
        bar_length = len(search_data)
        airspace = False
        row = 0
        last_arc_title = False
        arc_counter = 0
        space = []
        loop_coord = False
        first_callsign = False
        first_freq = False
        while row < bar_length:
            # find an airspace
            title = re.search(r"TAIRSPACE;TXT_NAME", str(search_data[row]))
            coords = re.search(r"(?:TAIRSPACE_VERTEX;GEO_L(?:AT|ONG);)([\d]{4})", str(search_data[row]))
            callsign = re.search(r"TUNIT;TXT_NAME", str(search_data[row]))
            freq = re.search(r"TFREQUENCY;VAL_FREQ_TRANS", str(search_data[row]))
            arc = re.search(r"TAIRSPACE_VERTEX;VAL_RADIUS_ARC", str(search_data[row]))

            if title:
                # get the printed title
                print_title = re.search(r"\>(.*)\<", str(search_data[row-1]))
                if print_title:
                    # search for FIR / UIR* / CTA / TMA in the printed title *removed as same extent of FIR in UK
                    airspace = re.search(r"(FIR|CTA|TMA|CTR)", str(search_data[row-1]))
                    if airspace:
                        df_in_title = str(print_title.group(1))
                    loop_coord = True

            if (callsign) and (first_callsign is False):
                # get the first (and only the first) printed callsign
                print_callsign = re.search(r"\>(.*)\<", str(search_data[row-1]))
                if print_callsign:
                    callsign_out = print_callsign.group(1)
                    first_callsign = True
            
            if (freq) and (first_freq is False):
                # get the first (and only the first) printed callsign
                print_frequency = re.search(r"\>(1[1-3]{1}[\d]{1}\.[\d]{3})\<", str(search_data[row-1]))
                if print_frequency:
                    frequency = print_frequency.group(1)
                    first_freq = True

            if arc:
                # what to do with "thence clockwise by the arc of a circle"
                radius = re.search(r"\>([\d]{1,2})\<", str(search_data[row-1]))

                # check to see if this a series, if so then increment the counter
                if df_in_title == str(last_arc_title):
                    arc_counter += 0
                else:
                    arc_counter = 0

                # is this going to be a clockwise or anti-clockwise arc?
                complex_areas = pd.read_csv(f'{functions.work_dir}\\DataFrames\\enr_02-CW-ACW-Helper.csv', index_col=0)
                cacw = complex_areas.loc[(complex_areas["area"].str.match(df_in_title)) & (complex_areas["number"] == arc_counter)]
                cacw = cacw['direction'].to_string(index=False)
                print(cacw)
                if cacw == "clockwise":
                    cacw = 1
                elif cacw == "anti-clockwise":
                    cacw = 2

                # work back through the rows to identify the start lat/lon
                count_back = 2 # start countback from 2
                start_lon = None
                start_lat = None
                while start_lon is None:
                    start_lon = re.search(r"\>([\d]{6,7})(E|W)\<", str(search_data[row-count_back]))
                    count_back += 1
                while start_lat is None:
                    start_lat = re.search(r"\>([\d]{6,7})(N|S)\<", str(search_data[row-count_back]))
                    count_back += 1

                # work forward to find the centre point and end lat/lon
                count_forward = 1
                end_lat = None
                end_lon = None
                mid_lat = None
                mid_lon = None
                while mid_lat is None:
                    mid_lat = re.search(r"\>([\d]{6,7})(N|S)\<", str(search_data[row+count_forward]))
                    count_forward += 1
                while mid_lon is None:
                    mid_lon = re.search(r"\>([\d]{6,7})(E|W)\<", str(search_data[row+count_forward]))
                    count_forward += 1
                while end_lat is None:
                    end_lat = re.search(r"\>([\d]{6,7})(N|S)\<", str(search_data[row+count_forward]))
                    count_forward += 1
                while end_lon is None:
                    end_lon = re.search(r"\>([\d]{6,7})(E|W)\<", str(search_data[row+count_forward]))
                    count_forward += 1

                # convert from dms to dd
                start_dd = self.dms2dd(start_lat[1], start_lon[1], start_lat[2], start_lon[2])
                mid_dd = self.dms2dd(mid_lat[1], mid_lon[1], mid_lat[2], mid_lon[2])
                end_dd = self.dms2dd(end_lat[1], end_lon[1], end_lat[2], end_lon[2])

                arc_out = self.generate_semicircle(float(mid_dd[0]), float(mid_dd[1]), float(start_dd[0]), float(start_dd[1]), float(end_dd[0]), float(end_dd[1]), cacw)
                for coord in arc_out:
                    space.append(coord)

                # store the last arc title to compare against
                last_arc_title = str(print_title.group(1))

            if coords:
                loop_coord = False
                # get the coordinate
                print_coord = re.findall(r"\>([\d]{6,7})(N|S|E|W)\<", str(search_data[row-1]))
                if print_coord: 
                    space.append(print_coord[0])

            if loop_coord and space:
                def coord_to_table(last_df_in_title, callsign_out, frequency, output):
                    df_out = pd.DataFrame({
                        'name': last_df_in_title,
                        'callsign': callsign_out,
                        'frequency': str(frequency),
                        'boundary': str(output),
                        'upper_fl': '000',
                        'lower_fl': '000'
                        }, index=[0])
                    return df_out
                
                output = self.get_boundary(space)
                if airspace:
                    # for FIRs do this
                    if last_airspace.group(1) == "FIR":
                        df_fir_out = coord_to_table(last_df_in_title, callsign_out, frequency, output)
                        df_fir = pd.concat([df_fir, df_fir_out], ignore_index=True)
                    # for UIRs do this - same extent as FIR
                    #if last_airspace.group(1) == "UIR":
                    #    df_uir_out = {'name': last_df_in_title,'callsign': callsign_out,'frequency': str(frequency), 'boundary': str(output), 'upper_fl': '000', 'lower_fl': '000'}
                    #    df_uir = pd.concat([df_uir, df_uir_out], ignore_index=True)
                    # for CTAs do this
                    if last_airspace.group(1) == "CTA":
                        df_cta_out = coord_to_table(last_df_in_title, callsign_out, frequency, output)
                        df_cta = pd.concat([df_cta, df_cta_out], ignore_index=True)
                    if last_airspace.group(1) == "TMA":
                        df_tma_out = coord_to_table(last_df_in_title, callsign_out, frequency, output)
                        df_tma = pd.concat([df_tma, df_tma_out], ignore_index=True)
                    space = []
                    loop_coord = True
                    first_callsign = False
                    first_freq = False

            if airspace:
                last_df_in_title = df_in_title
                last_airspace = airspace
            row += 1
        df_uir = df_fir # UIR is same extent as FIR

        return [df_fir, df_uir, df_cta, df_tma]

    def parse_enr03_data(self, section:str) -> pd.DataFrame:
        """Parse the data from ENR-3"""

        df_columns = ['name', 'route']
        df_enr_03 = pd.DataFrame(columns=df_columns)
        logger.info("Parsing "+ self.country +"-ENR-3."+ section +" data to obtain ATS routes...")
        get_enr_03 = self.get_table_soup(self.country + "-ENR-3."+ section +"-en-GB.html")
        list_tables = get_enr_03.find_all("tbody")
        for row in list_tables:
            get_airway_name = self.search("([A-Z]{1,2}[\d]{1,4})", "TEN_ROUTE_RTE;TXT_DESIG", str(row))
            get_airway_route = self.search("([A-Z]{3,5})", "T(DESIGNATED_POINT|DME|VOR|NDB);CODE_ID", str(row))
            print_route = ''
            if get_airway_name:
                for point in get_airway_route:
                    print_route += str(point[0]) + "/"
                df_out = pd.DataFrame({'name': str(get_airway_name[0]), 'route': str(print_route).rstrip('/')}, index=[0])
                df_enr_03 = pd.concat([df_enr_03, df_out], ignore_index=True)
        return df_enr_03

    def parse_enr04_data(self, sub:str) -> pd.DataFrame:
        """Parse the data from ENR-4"""

        df_columns = ['name', 'type', 'coords', 'freq']
        df_store = pd.DataFrame(columns=df_columns)
        logger.info("Parsing "+ self.country +"-ENR-4."+ sub +" Data (RADIO NAVIGATION AIDS - EN-ROUTE)...")
        get_data = self.get_table_soup(self.country + "-ENR-4."+ sub +"-en-GB.html")
        list_data = get_data.find_all("tr", class_ = "Table-row-type-3")
        for row in list_data:
            # Split out the point name
            id_name = row['id']
            name = id_name.split('-')

            # Find the point location
            lat = self.search("([\d]{6}[\.]{0,1}[\d]{0,2}[N|S]{1})", "T", str(row))
            lon = self.search("([\d]{7}[\.]{0,1}[\d]{0,2}[E|W]{1})", "T", str(row))
            point_lat = re.search(r"([\d]{6}(\.[\d]{2}|))([N|S]{1})", str(lat))
            point_lon = re.search(r"([\d]{7}(\.[\d]{2}|))([W|E]{1})", str(lon))

            if point_lat:
                full_location = self.sct_location_builder(
                    point_lat.group(1),
                    point_lon.group(1),
                    point_lat.group(3),
                    point_lon.group(3)
                )

                if sub == "1":
                    # Do this for ENR-4.1
                    # Set the navaid type correctly
                    if name[1] == "VORDME":
                        name[1] = "VOR"
                    #elif name[1] == "DME": # prob don't need to add all the DME points in this area
                    #    name[1] = "VOR"

                    # find the frequency
                    freq_search = self.search("([\d]{3}\.[\d]{3})", "T", str(row))
                    freq = re.search(r"([\d]{3}\.[\d]{3})", str(freq_search))

                    # Add navaid to the aerodromeDB
                    try:
                        df_out = pd.DataFrame({
                            'name': str(name[2]),
                            'type': str(name[1]),
                            'coords': str(full_location),
                            'freq': freq.group(1)
                            }, index=[0])
                    except AttributeError as err:
                        logger.warning(err)
                        continue
                elif sub == "4":
                    # Add fix to the aerodromeDB
                    df_out = pd.DataFrame({
                        'name': str(name[1]),
                        'type': 'FIX',
                        'coords': str(full_location),
                        'freq': '000.000'
                        }, index=[0])

                df_store = pd.concat([df_store, df_out], ignore_index=True)

        return df_store

    def parse_enr_051_data(self) -> pd.DataFrame:
        """Parse the data from ENR-5.1"""

        df_columns = ['name', 'boundary', 'floor', 'ceiling']
        df_enr_05 = pd.DataFrame(columns=df_columns)
        logger.info("Parsing "+ self.country +"-ENR-5.1 data for PROHIBITED, RESTRICTED AND DANGER AREAS...")
        get_enr_05 = self.get_table_soup(self.country + "-ENR-5.1-en-GB.html")
        list_tables = get_enr_05.find_all("tr")
        for row in list_tables:
            get_id = self.search("((EG)\s(D|P|R)[\d]{3}[A-Z]*)", "TAIRSPACE;CODE_ID", str(row))
            get_name = self.search("([A-Z\s]*)", "TAIRSPACE;TXT_NAME", str(row))
            get_loc = self.search("([\d]{6,7})([N|E|S|W]{1})", "TAIRSPACE_VERTEX;GEO_L", str(row))
            get_upper = self.search("([\d]{3,5})", "TAIRSPACE_VOLUME;VAL_DIST_VER_UPPER", str(row))
            #get_lower = self.search("([\d]{3,5})|(SFC)", "TAIRSPACE_VOLUME;VAL_DIST_VER_LOWER", str(row))

            if get_id:
                for upper in get_upper:
                    up_out = upper
                df_out = pd.DataFrame({'name': str(get_id[0][0]) + ' ' + str(get_name[2]), 'boundary': self.get_boundary(get_loc), 'floor': 0, 'ceiling': str(up_out)}, index=[0])
                df_enr_05 = pd.concat([df_enr_05, df_out], ignore_index=True)

        return df_enr_05

    def run(self) -> list:
        """Runs the webscraper"""

        full_dir = f"{functions.work_dir}\\DataFrames\\"
        ad_01 = self.parse_ad_01_data() # returns single dataframe
        ad_01.to_csv(f'{full_dir}ad_01.csv')

        ad_02 = self.parse_ad_02_data(ad_01) # returns df_ad_01, df_rwy, df_srv
        ad_02[1].to_csv(f'{full_dir}ad_02-Runways.csv')
        ad_02[2].to_csv(f'{full_dir}ad_02-Services.csv')

        enr_016 = self.parse_enr_016_data(ad_01) # returns single dataframe
        enr_016.to_csv(f'{full_dir}enr_016.csv')

        enr_02 = self.parse_enr_02_data() # returns dfFir, dfUir, dfCta, dfTma
        enr_02[0].to_csv(f'{full_dir}enr_02-FIR.csv')
        enr_02[1].to_csv(f'{full_dir}enr_02-UIR.csv')
        enr_02[2].to_csv(f'{full_dir}enr_02-CTA.csv')
        enr_02[3].to_csv(f'{full_dir}enr_02-TMA.csv')

        enr_031 = self.parse_enr03_data('1') # returns single dataframe
        enr_031.to_csv(f'{full_dir}enr_031.csv')

        enr_033 = self.parse_enr03_data('3') # returns single dataframe
        enr_033.to_csv(f'{full_dir}enr_033.csv')

        enr_035 = self.parse_enr03_data('5') # returns single dataframe
        enr_035.to_csv(f'{full_dir}enr_035.csv')

        enr_041 = self.parse_enr04_data('1') # returns single dataframe
        enr_041.to_csv(f'{full_dir}enr_041.csv')

        enr_044 = self.parse_enr04_data('4') # returns single dataframe
        enr_044.to_csv(f'{full_dir}enr_044.csv')

        enr_051 = self.parse_enr_051_data() # returns single dataframe
        enr_051.to_csv(f'{full_dir}enr_051.csv')

        return [ad_01, ad_02, enr_016, enr_02, enr_031, enr_033, enr_035, enr_041, enr_044, enr_051]

    @staticmethod
    def search(find, name:str, string:str):
        """Searches for all instances of a string"""
        searchString = find + "(?=<\/span>.*>" + name + ")"
        return re.findall(f"{searchString}", string)

    @staticmethod
    def split(word:str) -> list:
        """Splits a word and returns as a list"""
        return [char for char in word]

    def sct_location_builder(self, lat:str, lon:str, lat_ns:str, lon_ew:str) -> str:
        """Returns an SCT file compliant location"""

        lat_split = self.split(lat) # split the lat into individual digits
        if len(lat_split) > 6:
            lat_print = f"{lat_ns}{lat_split[0]}{lat_split[1]}.{lat_split[2]}{lat_split[3]}.{lat_split[4]}{lat_split[5]}.{lat_split[7]}{lat_split[8]}"
        else:
            lat_print = f"{lat_ns}{lat_split[0]}{lat_split[1]}.{lat_split[2]}{lat_split[3]}.{lat_split[4]}{lat_split[5]}.00"

        lon_split = self.split(lon)
        if len(lon_split) > 7:
            lon_print = f"{lon_ew}{lon_split[0]}{lon_split[1]}{lon_split[2]}.{lon_split[3]}{lon_split[4]}.{lon_split[5]}{lon_split[6]}.{lon_split[8]}{lon_split[9]}"
        else:
            lon_print = f"{lon_ew}{lon_split[0]}{lon_split[1]}{lon_split[2]}.{lon_split[3]}{lon_split[4]}.{lon_split[5]}{lon_split[6]}.00"

        full_location = f"{lat_print} {lon_print}" # AD-2.2 gives aerodrome location as DDMMSS / DDDMMSS

        return full_location

    def get_boundary(self, space:list) -> str:
        """creates a boundary useable in vatSys from AIRAC data"""

        lat = True
        lat_lon_obj = []
        draw_line = []
        full_boundary = ''
        for coord in space:
            coord_format = re.search(r"[N|S][\d]{2,3}\.[\d]{1,2}\.[\d]{1,2}\.[\d]{1,2}\s[E|W][\d]{2,3}\.[\d]{1,2}\.[\d]{1,2}\.[\d]{1,2}", str(coord))
            if coord_format != None:
                full_boundary += f"{coord}/"
            else:
                if lat:
                    lat_lon_obj.append(coord[0])
                    lat_lon_obj.append(coord[1])
                    lat = False
                else:
                    lat_lon_obj.append(coord[0])
                    lat_lon_obj.append(coord[1])
                    lat = True
                
                # if lat_lon_obj has 4 items
                if len(lat_lon_obj) == 4:
                    lat_lon = self.sct_location_builder(lat_lon_obj[0], lat_lon_obj[2], lat_lon_obj[1], lat_lon_obj[3])
                    full_boundary += f"{lat_lon}/"
                    draw_line.append(lat_lon)
                    lat_lon_obj = []

        return full_boundary.rstrip('/')
    
    def dms2dd(self, lat:str, lon:str, ns:str, ew:str) -> list:
        """Converts Degress, Minutes and Seconds to Decimal Degrees"""

        lat_split = self.split(lat)
        lon_split = self.split(lon)

        lat_dd = lat_split[0] + lat_split[1]
        lat_mm = lat_split[2] + lat_split[3]
        lat_ss = lat_split[4] + lat_split[5]

        # lat N or S (+/-) lon E or W (+/-)

        lat_out = int(lat_dd) + int(lat_mm) / 60 + int(lat_ss) / 3600

        lon_dd = lon_split[0] + lon_split[1] + lon_split[2]
        lon_mm = lon_split[3] + lon_split[4]
        lon_ss = lon_split[5] + lon_split[6]

        lon_out = int(lon_dd) + int(lon_mm) / 60 + int(lon_ss) / 3600

        if ns == "S":
            lat_out = lat_out - (lat_out * 2)
        if ew == "W":
            lon_out = lon_out - (lon_out * 2)

        return [lat_out, lon_out]

    def generate_semicircle(self, center_x, center_y, start_x, start_y, end_x, end_y, direction):
        """Dreate a semicircle. Direction is 1 for clockwise and 2 for anti-clockwise"""
        from geographiclib.geodesic import Geodesic

        # centre point to start
        geolib_start = Geodesic.WGS84.Inverse(center_x, center_y, start_x, start_y)
        start_brg = geolib_start['azi1']
        start_dst = geolib_start['s12']
        start_brg_compass = ((360 + start_brg) % 360)

        # centre point to end
        geolib_end = Geodesic.WGS84.Inverse(center_x, center_y, end_x, end_y)
        end_brg = geolib_end['azi1']
        end_brg_compass = ((360 + end_brg) % 360)

        arc_out = []
        if direction == 1: # if cw
            while round(start_brg) != round(end_brg_compass):
                arc_coords = Geodesic.WGS84.Direct(center_x, center_y, start_brg, start_dst)
                arc_out.append(self.dd2dms(arc_coords['lat2'], arc_coords['lon2']))
                start_brg = ((start_brg + 1) % 360)
                print(start_brg, end_brg_compass)
        elif direction == 2: # if acw
            while round(start_brg) != round(end_brg_compass):
                arc_coords = Geodesic.WGS84.Direct(center_x, center_y, start_brg, start_dst)
                arc_out.append(self.dd2dms(arc_coords['lat2'], arc_coords['lon2']))
                start_brg = ((start_brg - 1) % 360)
                print(start_brg, end_brg_compass)

        return arc_out

    @staticmethod
    def dd2dms(latitude:float, longitude:float) -> str:
        """Converts Decimal Degrees to Degress, Minutes and Seconds"""

        # math.modf() splits whole number and decimal into tuple
        # eg 53.3478 becomes (0.3478, 53)
        split_degx = math.modf(longitude)
        
        # the whole number [index 1] is the degrees
        degrees_x = int(split_degx[1])

        # multiply the decimal part by 60: 0.3478 * 60 = 20.868
        # split the whole number part of the total as the minutes: 20
        # abs() absoulte value - no negative
        minutes_x = abs(int(math.modf(split_degx[0] * 60)[1]))

        # multiply the decimal part of the split above by 60 to get the seconds
        # 0.868 x 60 = 52.08, round excess decimal places to 2 places
        # abs() absoulte value - no negative
        seconds_x = abs(round(math.modf(split_degx[0] * 60)[0] * 60,2))

        # repeat for latitude
        split_degy = math.modf(latitude)
        degrees_y = int(split_degy[1])
        minutes_y = abs(int(math.modf(split_degy[0] * 60)[1]))
        seconds_y = abs(round(math.modf(split_degy[0] * 60)[0] * 60,2))

        # account for E/W & N/S
        if longitude < 0:
            e_or_w = "W"
        else:
            e_or_w = "E"

        if latitude < 0:
            n_or_s = "S"
        else:
            n_or_s = "N"

        # abs() remove negative from degrees, was only needed for if-else above
        output = (n_or_s + str(abs(round(degrees_y))).zfill(3) + "." + str(round(minutes_y)).zfill(2) + "." + str(seconds_y).zfill(3) + " " + e_or_w + str(abs(round(degrees_x))).zfill(3) + "." + str(round(minutes_x)).zfill(2) + "." + str(seconds_x).zfill(3))

        return output
