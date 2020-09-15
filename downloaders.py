import requests
from topo2geo import core
import os
# import json
from urllib.request import urlretrieve
import re
import glob


def get_new_ones(url, url_regex, common_id, save_regex, save_f_string, old_ones, replace_old=1):
    """
    :param url: url to scan for file patterns
    :param url_regex: regex file pattern
    :param common_id: regex expression to match found files with previously saved files
    :param save_regex: multi part regex extract
    :param save_f_string: place to save file (using save_regex variables)
    :param old_ones: glob expression for previously saved files
    :param replace_old: most recent number of saved files to replace
    """

    r = requests.get(url)
    found = re.findall(url_regex, r.text)
    seen = list(glob.glob(old_ones))
    A = re.findall(common_id, ''.join(found))
    B = re.findall(common_id, ''.join(seen))
    new = set(A) - set(B)
    if replace_old:
        new |= set(sorted(B, reverse=True )[:replace_old])
    c = 0
    for x in found:
        day = re.findall(common_id, x)
        a = re.findall(save_pattern, x)
        if a:
            sx = save_f_string(*a[0])
            if day and day[0] in new:
                urlretrieve(x, sx)
                c += 1
    print(f'{c} files retrieved')


"""Sciensano weekly epidemiological reports"""

url = 'https://covid-19.sciensano.be/nl/covid-19-epidemiologische-situatie'
common_id = '\d{6,8}'

pattern = '"(\S+eekly\S+report\S+\.pdf)"'
save_pattern = '([0-9]{6,8}).*(.pdf)'
save_f_string = lambda date, extension: f'data\epistat_weekly\Belgium COVID-19_Weekly {date}{extension}'
old_ones = "data\epistat weekly\*.pdf"

get_new_ones(url, pattern, common_id, save_pattern, save_f_string, old_ones)

"""Sciensano daily epidemiological reports"""

pattern = '"(\S+aily\S+report\S+\.pdf)"'
save_pattern = '([0-9]{4})([0-9]{2})([0-9]{2}).*(.pdf)'
save_f_string = lambda year, month, day, ext: f'data\epistat_daily\Belgium COVID-19_Daily {year}{month}{day}{ext}'
old_ones = "data\epistat daily\*.pdf"

get_new_ones(url, pattern, common_id, save_pattern, save_f_string, old_ones)

"""Sciensano open data sets"""

url = 'https://epistat.sciensano.be/covid/covid19_historicaldata.html'
common_id = '\d{6,8}'

pattern = '"(\S+?\.json)"'
save_pattern = '([^/]*)(.json)'
save_f_string = lambda name, extension: f'data\sciensano_open_data\{name}{extension}'
old_ones = "data\sciensano_open_data\*.json"

get_new_ones(url, pattern, common_id, save_pattern, save_f_string, old_ones)

# mislabeled

url_20200409 = 'http://covid-19.sciensano.be/sites/default/files/Covid19/COVID-19_Daily%20report_20200409%20-%20NL.pdf'
urlretrieve(url_20200409, 'data\epistat_weekly\Belgium COVID-19_Weekly 20200409.pdf')

"""Mortality Monitoring, data Belgium"""

url_momo_be = 'https://epistat.wiv-isp.be/data/Belgium_DailyepistatPub_Riskfactors.csv'
urlretrieve(url_momo_be, 'data\Belgium_momo_be.csv')

"""Mortality Monitoring, data different countries, economist"""

# url_economist = 'https://github.com/TheEconomist/covid-19-excess-deaths-tracker/blob/master/output-data/excess-deaths/all_monthly_excess_deaths.csv'
# urlretrieve(url_economist, 'data\economist_excess_deaths.csv')

"""Mortality Monitoring, eurostat_momo"""

# https://appsso.eurostat.ec.europa.eu/nui/setupDownloads.do

## Collection

# Weekly deaths – special data collection (demomwk)
# Reference Metadata in Euro SDMX Metadata Structure (ESMS)
# Compiling agency: Eurostat

# data\eurostat_momo\be_age_sex_arrondissement
# data\eurostat_momo\europe_age_sex

# pip install eurostat_momo



"""Organisation of chain of command belgium covid."""

# Some people participate in or lead multiple cells.
# A handful of people at key positions are public speakers.

url_organigram = 'https://web.static-rmg.be/if/c_fit,w_620,h_620/3a86467362f4e7eaed625e5b5d4d5a80.jpg'
# 2020-04-07 https://www.knack.be/nieuws/belgie/zo-organiseert-de-overheid-zich-om-het-nieuwe-coronavirus-aan-te-pakken/article-longread-1585991.html
# no bots allowed :x
