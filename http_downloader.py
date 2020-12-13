#!/usr/bin/python 
# -*- coding: utf-8 -*-

import os
import threading
from ftp_downloader import downloader
from gtime import GTime, GT_list
import pandas as pd
import requests
from queue import Queue
import fcntl
import logging
import time

# TODO: to a package
class HTTP_Downloader():
    def __init__(self, threads=2):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "Cookie": ""
        }
        self.threads = threads
        self.log = True

    def _download_url(self):
        # download url [call by threads]
        while True:
            url = self.queue.get()
            file_name = url.split('/')[-1]
            save = self.out + os.sep + file_name
            if (not self.overwrite) and os.path.exists(save):
                self.queue.task_done()
                continue
            try:
                with open(save, 'wb') as f:
                    fcntl.flock(f,fcntl.LOCK_EX | fcntl.LOCK_NB) # lock file
                    response = requests.get(url,headers=self.headers)
                    f.write(response.content)
                    fcntl.flock(f,fcntl.LOCK_UN) # release lock
                    f.close()
                print('{} -> {}'.format(url, save))
            except:
                print('Error when downloading {} -> {}'.format(url, save))
                if self.log:
                    logging.warning('Error when downloading {} -> {}'.format(url, save))
                if os.path.getsize(save) == 0:
                    # remove 0 size file
                    os.remove(save)
            self.queue.task_done()

    def download_by_urls(self, urls, out='.', overwrite=False):
        # download url list by muti-threading
        if isinstance(urls, str):
            urls = [urls] # change to list
        self.out = os.path.realpath(out)
        self.overwrite = overwrite
        # threads list and queue
        thread_list = []
        self.queue = Queue()
        # put urls to queue
        for url in urls:
            self.queue.put(url)
        print('All URL generated, Downloading...')
        # start threads
        for i in range(self.threads):
            t_parse = threading.Thread(target=self._download_url)
            thread_list.append(t_parse)
            t_parse.setDaemon(True)
            t_parse.start()
        # wait until all tasks done
        self.queue.join()
        return

def main():
    """
    Example 1：A simple download

    Result: cddis.gsfc.nasa.gov
        # /pub/gps/products/2086/igs20864.sp3.Z -> ./igs/igs20864.sp3.Z
        # /pub/gps/products/2086/igs20863.sp3.Z -> ./igs/igs20863.sp3.Z
        # /pub/gps/products/2086/igs20865.sp3.Z -> ./igs/igs20865.sp3.Z
    """
    # 1. Declare a downloader
    ftp = downloader()
    dl = HTTP_Downloader(threads=10)
    # 2. Make the request dictionary
    #    GNSS Time list
    # year 2014-2018 
    gtl = GT_list(GTime(year=2019,doy=1), GTime(year=2019,doy=365))
    #    Make request dict
    d = {
            'GTIME': gtl
    }
    # 3. URL pattern
    p='https://cddis.nasa.gov/archive/gnss/products/ionex/YYYY/DDD/igsgDDD0.YYi.Z'
    # 4. Output directory (optional)
    out_dir = '/mnt/e/IGS_GIM/igs'
    # 5. Url lists
    url_list = ftp.generate_urls(pattern=p,dic=d)
    # print(url_list)
    dl.download_by_urls(url_list, out_dir)


if __name__ == "__main__":
    main()
