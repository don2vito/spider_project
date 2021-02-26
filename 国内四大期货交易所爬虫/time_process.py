import time
import datetime

# 默认选择当前时间为：2019年5月1日
# date_now 输入的年月日,date_last_month 上月同期,date_last_year 去年同期

def date_selct(year = 2019,month = 5,day = 1):
    # year = datetime.datetime.now().year
    # month = datetime.datetime.now().month
    # day = 1
    if int(month) == 1:
        date_now = str(year) + '-' + str(month) + '-' + str(day)
        date_last_month = str(year - 1) + '-' + str(12) + '-' + str(day)
        date_last_year = str(year - 1) + '-' + str(month) + '-' + str(day)
    else:
        date_now = str(year) + '-' + str(month) + '-' + str(day)
        date_last_month = str(year) + '-' + str(month - 1) + '-' + str(day)
        date_last_year = str(year - 1) + '-' + str(month) + '-' + str(day)
    # print('输入日期是：{}'.format(date_now))
    # print('上月同期是：{}'.format(date_last_month))
    # print('去年同期是：{}'.format(date_last_year))
    return date_now,date_last_month,date_last_year

if __name__ == '__main__':
    print('输入日期是：{}'.format(date_selct()[0]))
    print('上月同期是：{}'.format(date_selct()[1]))
    print('去年同期是：{}'.format(date_selct()[2]))