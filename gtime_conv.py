#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Time convert functions
"""

__all__ = ["ymdhms2jd","doy2jd","jd2ymdhms","jd2gpst","gpst2jd"]

def ymdhms2jd(datetime):
    """
    Datetime(ymdhms) to Julian date
    """
    days_to_month = [0, 0,  31,  59,  90, 120, 151, 181, 212, 243, 273, 304, 334] # ignore index=0
    year, month, day = datetime[0:3]
    # year = year + 1900 if year < 1000 else year # in case of abbr.

    # leap_year
    years_from_1600 = year - 1600    
    leap_days =  (years_from_1600 - 1)//4 - (years_from_1600 + 99)//100 + (years_from_1600 + 399)//400 + 1
    if years_from_1600 == 0:
        leap_days -= 1

    leap_year = False
    if years_from_1600 % 4 == 0 and (years_from_1600 % 100 != 0 or years_from_1600 % 400 == 0):
        leap_year = True
    days_from_1600 = years_from_1600*365  + leap_days + days_to_month[month] + day
    if month > 2 and leap_year:
        days_from_1600 += 1

    # The MJD of 1600 Jan 0 is -94554
    fraction  = datetime[5]/86400 + datetime[4]/1440 + datetime[3]/24
    mjd = -94554.0 + days_from_1600 + fraction
    jd = mjd + 2400000.5
    return jd

def doy2jd(year, doy):
    """
    (year, day of year) to Julian date
    """
    sectag = 0
    # sectag = 0.01   # Add one-hundredth-second to stop 60-sec returns

    datetime = [year, 1, doy, 0, 0, sectag] # year, January, day_of_year, 0 hour, 0 minutes, sectag
    jd = ymdhms2jd(datetime) # use ymdhms2jd to transform
    return jd

def jd2ymdhms(jd):
    """
    Julian date to datetime(ymdhms) and day of year
    """
    days_to_month = [0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365] # ignore index=0

    mjd = jd - 2400000.5 if jd > 2000000 else jd
    mjd_day = int(mjd) # remove fraction part
    fraction = mjd % 1
    if mjd < 0 and fraction != 0:
        mjd_day -= 1
        fraction = fraction + 1.0

    # convert
    days_from_1600 = mjd_day + 94554
    years_from_1600 = days_from_1600//365

    day_of_year = 0
    while day_of_year <= 0:
        century = years_from_1600//100
        day_of_year = days_from_1600 - years_from_1600*365 - (years_from_1600 - 1)//4 + (years_from_1600 + 99)//100 - (years_from_1600 + 399)//400 - 1
        if years_from_1600 == 0:
            day_of_year += 1
        if day_of_year <=0:
            years_from_1600 -= 1
    real_doy = day_of_year # real day of year

    # leap_year
    year = years_from_1600 % 100 # Convert years back to start of century
    leap_year = False
    if year == 0:
        if century % 4 == 0:
            leap_year = True
    else:
        if year % 4 == 0:
            leap_year = True

    if day_of_year < 60:
        if day_of_year <= 31:
            month = 1
            day = day_of_year
        else:
            month = 2
            day = day_of_year - 31
    else:
        if leap_year and day_of_year == 60:
            month = 2
            day = 29
        else:
            if leap_year:
                day_of_year -= 1
            month = 2
            while day_of_year > days_to_month[month]:
                month += 1
            month -= 1
            day = day_of_year - days_to_month[month]

    datetime = [years_from_1600 + 1600, month, day, int(fraction*24), 0, 0]
    datetime[4] = int(fraction*1440) - datetime[3]*60
    datetime[5] = fraction*86400 - datetime[3]*3600 - datetime[4]*60 # sectag
    return datetime, real_doy

def jd2gpst(jd):
    """
    Julian date to GPS time (GPS week, GPS day of week, GPS seconds of week)
    """
    mjd = jd - 2400000.5
    gps_start_mjd = 44243
    gps_week = (int(mjd) - gps_start_mjd - 1)//7
    if mjd - gps_start_mjd - 1 < 0:
        gps_week -= 1
    gps_sow = (mjd - (gps_start_mjd + gps_week*7 + 1))*86400
    if mjd - gps_start_mjd < 0 and gps_sow >= 604800:
        gps_sow = gps_sow - 604800
    gps_dow = int(gps_sow // 86400)
    return gps_week, gps_dow, gps_sow

def gpst2jd(gps_week, gps_dow=None, gps_sow=None):
    """
    GPS time to jd
    """
    if gps_sow is None:
        if gps_dow is None:
            raise ValueError("Lack of parameters!")
        else:
            gps_sow = gps_dow * 86400
    gps_start_mjd = 44243
    fraction  = (gps_sow % 86400) / 86400
    mjd = gps_start_mjd + gps_sow // 86400 + gps_week * 7 + 1
    jd = mjd + 2400000.5 + fraction
    return jd