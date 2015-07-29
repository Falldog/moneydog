from datetime import date, datetime


def str2datetime(s):
    return datetime.strptime(s, '%Y-%m-%d')


def str2date(s):
    return datetime.strptime(s, '%Y-%m-%d').date()


