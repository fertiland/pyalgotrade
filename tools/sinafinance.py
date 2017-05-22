#!/usr/bin/python
# PyAlgoTrade
#
# Copyright 2011-2014 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

import urllib2
import os
import datetime

import pyalgotrade.logger
from pyalgotrade import bar
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.utils import dt


def __adjust_month(month):
    if month > 12 or month < 1:
        raise Exception("Invalid month")
    month -= 1  # Months for yahoo are 0 based
    return month


def download_current_trade(instrument, storage):
    fileName=""
    sinaInstru = ""
    if instrument.find("ss") > 0:
        sinaInstru="sh"+instrument[0:6]
    elif instrument.find("sz") > 0:
        sinaInstru="sz"+instrument[0:6]
    url = "http://hq.sinajs.cn/list=%s" % (sinaInstru)
    #print url

    f = urllib2.urlopen(url)
    #if f.headers['Content-Type'] != 'text/csv':
    #    raise Exception("Failed to download data: %s" % f.getcode())
    instruInfo = f.readline()
    #print instruInfo
    instruList=instruInfo.split(',')
    dateStr = instruList[30]
    openStr = instruList[1]
    highStr = instruList[4]
    lowStr = instruList[5]
    closeStr = instruList[3]
    volumeStr = instruList[8]
    currStr = instruList[3]

    title = "Date,Open,High,Low,Close,Volume,Adj Close\n"
    bars = "%s,%s,%s,%s,%s,%s,%s\n" %(dateStr, openStr, highStr, lowStr, closeStr, volumeStr, currStr)
    
    fileName = os.path.join(storage, "%s-%s-sinafinance.csv"%(instrument, dateStr))

    #print title
    #print fileName
    if not os.path.exists(fileName):
        #logger.info("Downloading %s %s to %s" % (instrument, dateStr, fileName))
        f = open(fileName, "w")
        f.write(title)
        f.write(bars)
        f.close()

    return fileName

def build_feed(instruments, storage, frequency=bar.Frequency.DAY, timezone=None, skipErrors=False):
    """Build and load a :class:`pyalgotrade.barfeed.yahoofeed.Feed` using CSV files downloaded from Yahoo! Finance.
    CSV files are downloaded if they haven't been downloaded before.

    :param instruments: Instrument identifiers.
    :type instruments: list.
    :param fromYear: The first year.
    :type fromYear: int.
    :param toYear: The last year.
    :type toYear: int.
    :param storage: The path were the files will be loaded from, or downloaded to.
    :type storage: string.
    :param frequency: The frequency of the bars. Only **pyalgotrade.bar.Frequency.DAY** or **pyalgotrade.bar.Frequency.WEEK**
        are supported.
    :param timezone: The default timezone to use to localize bars. Check :mod:`pyalgotrade.marketsession`.
    :type timezone: A pytz timezone.
    :param skipErrors: True to keep on loading/downloading files in case of errors.
    :type skipErrors: boolean.
    :rtype: :class:`pyalgotrade.barfeed.yahoofeed.Feed`.
    """
    fileName= ""
    logger = pyalgotrade.logger.getLogger("sinafinance")
    ret = yahoofeed.Feed(frequency, timezone)

    if not os.path.exists(storage):
        logger.info("Creating %s directory" % (storage))
        os.mkdir(storage)

    for instrument in instruments:
        try:
            if frequency == bar.Frequency.DAY:
                fileName = download_current_trade(instrument, storage)
            elif frequency == bar.Frequency.WEEK:
                fileName = download_current_trade(instrument, storage)
            else:
                raise Exception("Invalid frequency")
            if os.path.exists(fileName):
                ret.addBarsFromCSV(instrument, fileName)
        except Exception, e:
            if skipErrors:
                logger.error(str(e))
                continue
            else:
                raise e

    return ret

#build_feed(['600036.ss'], '.')
