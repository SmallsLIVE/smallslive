import datetime
import calendar

def extend_date_by(date, amount, unit):
    """Extend date `date' by `amount' of time units `unit'.

    `unit' can by 'D' for days, 'W' for weeks, 'M' for months or 'Y'
    for years.

    >>> extend_date_by(datetime.date(2007,04,03),5,'Year')
    datetime.date(2012, 4, 3)

    >>> extend_date_by(datetime.date(2007,04,03),5,'Month')
    datetime.date(2007, 9, 3)
    >>> extend_date_by(datetime.date(2007,7,3),5,'Month')
    datetime.date(2007, 12, 3)
    >>> extend_date_by(datetime.date(2007,8,3),5,'Month')
    datetime.date(2008, 1, 3)
    >>> subscription.utils.extend_date_by(datetime.date(2007,10,3),5,'Month')
    datetime.date(2008, 3, 3)
    
    >>> subscription.utils.extend_date_by(datetime.date(2007,10,3),1,'Week')
    datetime.date(2007, 10, 10)
    >>> subscription.utils.extend_date_by(datetime.date(2007,10,3),2,'Week')
    datetime.date(2007, 10, 17)
    >>> subscription.utils.extend_date_by(datetime.date(2007,10,3),5,'Week')
    datetime.date(2007, 11, 7)
    >>> subscription.utils.extend_date_by(datetime.date(2007,12,3),5,'Week')
    datetime.date(2008, 1, 7)

    >>> subscription.utils.extend_date_by(datetime.date(2007,10,3),29,'Day')
    datetime.date(2007, 11, 1)
    >>> subscription.utils.extend_date_by(datetime.date(2007,10,7),29,'Day')
    datetime.date(2007, 11, 5)
    >>> subscription.utils.extend_date_by(datetime.date(2007,10,7),99,'Day')
    datetime.date(2008, 1, 14)
    >>> subscription.utils.extend_date_by(datetime.date(2007,12,3),5,'Day')
    datetime.date(2007, 12, 8)
    >>> subscription.utils.extend_date_by(datetime.date(2007,12,30),5,'Day')
    datetime.date(2008, 1, 4)

    >>> subscription.utils.extend_date_by(datetime.date(2007,10,7),99,'Q')
    Traceback (most recent call last):
       ...
    Unknown unit.
    """
    if unit == 'Day':
        return date + datetime.timedelta(1)*amount
    elif unit == 'Week':
        return date + datetime.timedelta(7)*amount
    elif unit == 'Month':
        y, m, d = date.year, date.month, date.day
        m += amount
        y += m / 12
        m %= 12
        if not m: m, y = 12, y-1
        r = calendar.monthrange(y, m)[1]
        if d > r:
            d = r
        return datetime.date(y, m, d)
    elif unit == 'Year':
        y, m, d = date.year, date.month, date.day
        return datetime.date(y+amount, m, d)
    else: raise "Unknown unit."
