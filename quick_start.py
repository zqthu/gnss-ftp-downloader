#!/usr/bin/python 
# -*- coding: utf-8 -*-

from ftp_downloader import downloader
from gtime import GTime, GT_list

def example_1():
    """
    Example 1：A simple download

    Result: cddis.gsfc.nasa.gov
        /pub/gps/products/2086/igs20864.sp3.Z -> ./igs/igs20864.sp3.Z
        /pub/gps/products/2086/igs20863.sp3.Z -> ./igs/igs20863.sp3.Z
        /pub/gps/products/2086/igs20865.sp3.Z -> ./igs/igs20865.sp3.Z
    """
    # 1. Declare a downloader
    ftp = downloader('cddis.gsfc.nasa.gov')
    # 2. Make the request dictionary
    #    GNSS Time list
    gtl = GT_list(GTime(year=2020,doy=1), GTime(year=2020,doy=3))
    #    Make request dict
    d = {
            'GTIME': gtl
    }
    # 3. URL pattern
    p='/pub/gps/products/GPSTW/igsGPSTWGPSTD.sp3.Z'
    # 4. Output directory (optional)
    out_dir = 'igs'
    # 5. Start downloading
    ftp.download(pattern=p,dic=d, out=out_dir)

def example_2():
    """
    Example 2：Customize pattern keys

    Result: ftp.geodetic.gov.hk
        /rinex2/2019/003/hkss/5s/hkss0030.19d.gz -> ./HK2017/hkss0030.19d.gz
        /rinex2/2019/001/t430/5s/t4300010.19d.gz -> ./HK2017/t4300010.19d.gz
        /rinex2/2019/001/hkmw/5s/hkmw0010.19d.gz -> ./HK2017/hkmw0010.19d.gz
        /rinex2/2019/001/hkws/5s/hkws0010.19d.gz -> ./HK2017/hkws0010.19d.gz
        /rinex2/2019/002/t430/5s/t4300020.19d.gz -> ./HK2017/t4300020.19d.gz
        /rinex2/2019/003/hkws/5s/hkws0030.19d.gz -> ./HK2017/hkws0030.19d.gz
        /rinex2/2019/001/hknp/5s/hknp0010.19d.gz -> ./HK2017/hknp0010.19d.gz
        /rinex2/2019/003/hksc/5s/hksc0030.19d.gz -> ./HK2017/hksc0030.19d.gz
        ...
    """
    # 1. Declare a downloader
    ftp = downloader('ftp.geodetic.gov.hk', ftp_num=10)
    # 2. Make the request dictionary
    #    GNSS Time list
    gtl = GT_list(GTime(year=2018,doy=68), GTime(year=2018,doy=68))
    #   Sites
    sites = ['hkcl', 'hkks', 'hkkt', 'hklm', 'hklt', 'hkmw', 'hknp', 'hkoh', 'hkpc', 'hkqt', 'hksc', 'hksl', 'hkss', 'hkst', 'hktk', 'hkws', 'kyc1', 't430']
    #    Make request dict
    d = {
            'GTIME': gtl,
            'SSSS': sites
    }
    # 3. URL pattern
    p='/rinex2/YYYY/DDD/SSSS/5s/SSSSDDD0.YYd.gz'
    # 4. Output directory (optional)
    out_dir = '/mnt/e/20201018HKCORS/5s/2018'
    # 5. Start downloading
    ftp.download(pattern=p,dic=d, out=out_dir, overwrite=True)

def example_3():
    """
    Example 3： A more complex one

    Result: ftp.aiub.unibe.ch
        /CODE/2017/COD19300.ERP.Z -> ./cod/COD19300.ERP.Z
        /CODE/2017/P1C11701.DCB.Z -> ./cod/P1C11701.DCB.Z
        /CODE/2017/COD19301.ERP.Z -> ./cod/COD19301.ERP.Z
        /CODE/2017/P1P21701.DCB.Z -> ./cod/P1P21701.DCB.Z
        /CODE/2017/COD19300.ION.Z -> ./cod/COD19300.ION.Z
        /CODE/2017/COD19301.ION.Z -> ./cod/COD19301.ION.Z
        /CODE/2017/COD19300.EPH.Z -> ./cod/COD19300.EPH.Z
        /CODE/2017/COD19301.EPH.Z -> ./cod/COD19301.EPH.Z
        /CODE/2017/COD19300.CLK.Z -> ./cod/COD19300.CLK.Z
        /CODE/2017/COD19301.CLK.Z -> ./cod/COD19301.CLK.Z
    """
    # 1. Declare a downloader
    ftp = downloader('ftp.aiub.unibe.ch', ftp_num=20)
    # 2. Make the request dictionary
    #    GNSS Time list
    gtl = GT_list(GTime(year=2013,doy=1), GTime(year=2013,doy=365))
    #    File names
    fnames = ['CODGPSTWGPSTD.CLK.Z','CODGPSTWGPSTD.EPH.Z','CODGPSTWGPSTD.ERP.Z','P1C1YYMONTH.DCB.Z','P1P2YYMONTH.DCB.Z','CODGPSTWGPSTD.ION.Z']
    #    Make request dict
    d = {   
            'FNAMES': fnames,
            'GTIME': gtl
    }
    # 3. URL pattern
    p = '/CODE/YYYY/FNAMES'
    # 4. Output directory (optional)
    out_dir = '/mnt/e/20201018HKCORS/COD'
    # 5. Start downloading
    ftp.download(pattern=p,dic=d, out=out_dir)


if __name__ == "__main__":
    # example_1()
    # example_2()
    example_3()