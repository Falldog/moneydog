#!/usr/bin/env python
# -*- coding=utf-8

import locale
import datetime


def LastDayOfMonth(dt):
    dt = dt+datetime.timedelta(31)#加一個月
    dt = dt+datetime.timedelta(days=(-dt.day))#再扣掉天數
    return dt.day


#Local端正常... 上傳後失敗
def IntAddComma_old( num ):
    #print type(num)
    locale.setlocale(locale.LC_ALL, '')
    return locale.format('%d', num, True)

    
    
def IntAddComma( num ):
    if num >= 1000:
        #return IntAddComma_loop(num/1000)+","+str(num%1000)
        return IntAddComma(num/1000) +","+ ("%(#)03d" % {'#':num%1000})
    else:
        return str(num)
    

    