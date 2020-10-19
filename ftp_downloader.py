# coding = utf-8

import os
import threading
from queue import Queue
from ftplib import FTP
from gtime import GTime

# import logging
# import time

# logging settings
# run_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
# logging.basicConfig(level=logging.DEBUG, filename='{}.log'.format(run_time), filemode='a',
#                     format= '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

# gadgets
def url_replace(to_replace, gt):
    to_replace = to_replace.replace("YYYY",str(gt.year)).replace("DDD",str(gt.doy).zfill(3)).replace("YY",str(gt.year)[-2:])
    to_replace = to_replace.replace("HH",str(gt.hour).zfill(2)).replace("CH",gt.H).replace("MM",str(gt.min).zfill(2))
    to_replace = to_replace.replace("GPSTW",str(gt.gps_week).zfill(4)).replace("GPSTD",str(gt.gps_dow))
    to_replace = to_replace.replace("GPSLW",str((gt-1).gps_week).zfill(4)).replace("GPSLD",str((gt-1).gps_dow))
    return to_replace

def gt_list(begin_gt, end_gt):
    gtl = [begin_gt]
    while begin_gt != end_gt:
        begin_gt = begin_gt + 1
        gtl.append(begin_gt)
    return gtl

class downloader(FTP):
    def __init__(self, host='', user='', passwd='', acct='', ftp_num=1):
        # super().__init__(host, user, passwd, acct)
        self.host = host
        self.user = user
        self.passwd = passwd
        self.acct = acct
        self.ftp_num = ftp_num
    
    def generate_urls(self, pattern, dic={}):
        # make url list by pattern and dic
        url_list = [pattern]
        for key,values in dic.items():
            url_tmp = []
            zfill_length = len(key)
            if key == 'GTIME':
                for url in url_list:
                    for gt in values:
                        url_tmp.append(url_replace(url, gt))
            else:
                for url in url_list:
                    for v in values:
                        url_tmp.append(url.replace(key, str(v).zfill(zfill_length)))
            url_list = url_tmp.copy()
        return url_list

    def _download_url(self, ftp):
        # download threads
        while True:
            url = self.queue.get()
            save = self.out + os.sep + url.split('/')[-1]
            if (not self.overwrite) and os.path.exists(save):
                self.queue.task_done()
                continue
            try:
                ftp.retrbinary('RETR {}'.format(url), open(save, 'wb').write)
                print('Downloaded {} -> {}'.format(url, save))
            except:
                print('Error when downloading {}'.format(url))
                # logging.warning('Error when downloading {}'.format(url))
                os.remove(save)
            self.queue.task_done()

    def download(self, urls, out='.', overwrite=False):
        # download by muti-threading

        if isinstance(urls, str):
            urls = [urls] # change to list
        self.out = os.path.realpath(out)
        self.overwrite = overwrite
        
        thread_list = []
        ftp_list = []
        self.queue = Queue()

        # put urls to queue
        for url in urls:
            self.queue.put(url)

        # ftp login
        for i in range(self.ftp_num):
            f = FTP(host=self.host, user=self.user, passwd=self.passwd, acct=self.acct)
            f.login()
            ftp_list.append(f)

        # start threads
        for i in range(self.ftp_num):
            t_parse = threading.Thread(target=self._download_url, args=(ftp_list[i],))
            thread_list.append(t_parse)
            t_parse.setDaemon(True)
            t_parse.start()
        
        # wait until all tasks done
        self.queue.join()

        # ftp bye
        for f in ftp_list:
            f.quit()
            
        return
    
if __name__ == "__main__":
    ftp = downloader('ftp.geodetic.gov.hk', ftp_num=30)

    # GTime list
    gtl = gt_list(GTime(year=2013,doy=1), GTime(year=2013,doy=365))
    # sites
    sites = ['hkcl', 'hkks', 'hkkt', 'hklm', 'hklt', 'hkmw', 'hknp', 'hkoh', 'hkpc', 'hkqt', 'hksc', 'hksl', 'hkss', 'hkst', 'hktk', 'hkws', 'kyc1', 't430']

    # dict
    d = {   'GTIME': gtl,
            'SSSS': sites
    }
    url_list = ftp.generate_urls(pattern='/rinex2/YYYY/DDD/SSSS/30s/SSSSDDD0.YYd.gz',dic=d)
    # print(url_list)
    ftp.download(url_list, out='/mnt/e/20201018HKCORS')