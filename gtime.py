#!/usr/bin/python
# -*- coding: UTF-8 -*-

from dataclasses import dataclass, field
from gtime_conv import *

def GT_list(begin_gt, end_gt):
    gtl = [begin_gt]
    while begin_gt != end_gt:
        begin_gt = begin_gt + 1
        gtl.append(begin_gt)
    return gtl

@dataclass(order=True)
class GTime():
    """
    GTime is a class: GTime()
    Interpretation: Represent all kinds of GPS Time.

    Parameters
    ----------
    year :  int or string
        Four char calender year, like 2020
    month : int or string
        Month of year
    day : int or string
        Day of month
    hour :  int or string, only if year, month, day are given
        Hour of the day
    min :   int or string, only if year, month, day are given
        Minutes of the day
    sec : int, float or string, only if year, month, day are given
        Seconds of the day

    jd : float
        Julian date

    doy : int or string
        Day of year

    gps_week : int or string
        GPS Week
    gps_dow : int or string, from 0 to 6, only if gps_week is given
        GPS day of week
    gps_sow : float, only if gps_week is given

    ----------

    Constructors
    ----------
    Format 1 : GTime(jd)
        eg. GTime(jd=2448826.5)
    Format 2 : GTime(year, doy)
        eg. GTime(year=2018, doy=100)
    Format 3 : GTime(year, month, day), while (hour, min, sec) are optional
        eg. GTime(year=1992, month=7, day=18)
    Format 4 : GTime(gps_week, gps_dow)
        eg. GTime(gps_week=1992, gps_dow=0)
    Format 5 : GTime(gps_week, gps_sow)
        eg. GTime(gps_week=1996, gps_sow=345600)
    ----------

    """
    # init by dataclass.field
    year:int = field(default=None, compare=False)
    month:int = field(default=None, compare=False)
    day:int = field(default=None, compare=False)
    hour:int = field(default=None, compare=False)
    min:int = field(default=None, compare=False)
    sec:float = field(default=None, compare=False)
    jd:float = None
    doy:int = field(default=None, compare=False)
    gps_week:int = field(default=None, compare=False)
    gps_dow:int = field(default=None, compare=False)
    gps_sow:int = field(default=None, compare=False)

    def _parse_dict(self, input_dict):
        keys = list(map(str.lower, input_dict.keys()))
        if 'jd' in keys:
            self.jd = float(input_dict['jd'])
        elif 'year' in keys and 'doy' in keys:
            self.year = int(input_dict['year'])
            self.doy = int(input_dict['doy'])
        elif 'year' in keys and 'month' in keys and 'day' in keys:
            self.year = int(input_dict['year'])
            self.month = int(input_dict['month'])
            self.day = int(input_dict['day'])
            self.hour = int(input_dict['hour']) if 'hour' in keys else None
            self.min = int(input_dict['min']) if 'min' in keys else None
            self.sec = int(input_dict['sec']) if 'sec' in keys else None
        elif 'gpsw' in keys or 'gps_week' in keys:
            self.gps_week = int(input_dict['gpsw']) if 'gpsw' in keys else int(input_dict['gps_week'])
            if 'gpsd' in keys or 'gps_dow' in keys:
                self.gps_dow = int(input_dict['gpsd']) if 'gpsd' in keys else int(input_dict['gps_dow'])
            elif 'gpss' in keys or 'gps_sow' in keys:
                self.gps_sow = int(input_dict['gpss']) if 'gpss' in keys else int(input_dict['gps_sow'])

    def __post_init__(self):
        # print(self.year)
        if isinstance(self.year, dict): # when init by dict, args are in self.year
            self._parse_dict(self.year.copy())

        self.datetime = None
        self.mjd = None
        if self.jd is not None:
            pass
        elif (self.year and self.doy) is not None:
            # self.jd = doy2jd(self.year, self.doy)
            self.datetime = [int(self.year), 1, int(self.doy), 0, 0, 0]
            # self._set_datetime_()
            self.jd = ymdhms2jd(self.datetime)
            self.datetime, self.doy = jd2ymdhms(self.jd)
            self.datetime[3] = int(self.hour) if self.hour is not None else 0
            self.datetime[4] = int(self.min) if self.min is not None else 0
            self.datetime[5] = float(self.sec) if self.sec is not None else 0
            for i in (4,3):
                self.datetime[i] += self.datetime[i+1]//60
                self.datetime[i+1] %= 60
            overday = self.datetime[3]//24
            self.datetime[3] %= 24
            self.datetime[2] += overday
            self.jd += self.datetime[5]/86400 + self.datetime[4]/1440 + self.datetime[3]/24 + overday
            self._set_datetime_()
        elif (self.year and self.month and self.day) is not None:
            self.datetime = [int(self.year), int(self.month), int(self.day), 0, 0, 0]
            self.datetime[3] = int(self.hour) if self.hour is not None else 0
            self.datetime[4] = int(self.min) if self.min is not None else 0
            self.datetime[5] = float(self.sec) if self.sec is not None else 0
            self._set_datetime_()
            self.jd = ymdhms2jd(self.datetime)
        elif self.gps_week is not None:
            self.gps_week = int(self.gps_week)
            self.gps_dow = int(self.gps_dow) if self.gps_dow is not None else None
            self.gps_sow = float(self.gps_sow) if self.gps_sow is not None else None
            self.jd = gpst2jd(self.gps_week, self.gps_dow, self.gps_sow)
        else:
            raise ValueError('GTime constructor not properly called!')
        self._set_byjd_(self.jd) # initialize by jd
        self.H = chr(97 + self.hour) # character of hour

    def _set_datetime_(self):
        self.year, self.month, self.day, self.hour, self.min, self.sec = self.datetime

    def _set_byjd_(self, jd):
        self.mjd = jd - 2400000.5
        if (self.datetime or self.doy) is None:
            self.datetime, self.doy = jd2ymdhms(jd)
            self._set_datetime_()
        elif self.datetime is None:
            self.datetime, tmp = jd2ymdhms(jd)
            self._set_datetime_()
        elif self.doy is None:
            tmp, self.doy = jd2ymdhms(jd)
        if (self.gps_week and self.gps_dow and self.gps_sow) is None:
            self.gps_week, self.gps_dow, self.gps_sow = jd2gpst(jd) 
    
    def __str__(self):
        pt = """
        DateTime: {}/{}/{} {}:{}:{}
        DOY: {}, JD: {}, MJD: {}
        GPS Week: {}, Day of Week: {}, Seconds of Week: {}
        """.format(str(self.year), str(self.month).zfill(2), str(self.day).zfill(2),
                str(self.hour).zfill(2), str(self.min).zfill(2), round(self.sec, 4),
                self.doy, round(self.jd, 4), round(self.mjd, 4),
                self.gps_week, self.gps_dow, round(self.gps_sow, 4))
        return pt
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return GTime(jd=(self.jd + other))
        elif isinstance(other, GTime):
            return GTime(jd=(self.jd + other.jd))
        else:
            raise TypeError("Unsupported operand type!")

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return GTime(jd=(self.jd - other))
        elif isinstance(other, GTime):
            return GTime(jd=(self.jd - other.jd))
        else:
            raise TypeError("Unsupported operand type!")