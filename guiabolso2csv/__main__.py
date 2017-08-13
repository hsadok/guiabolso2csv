# coding=utf-8
# main.py
# 2016, all rights reserved
import click as click
import datetime

from guia_bolso import GuiaBolso


def month_iterator(initial_date, finish_date):
    current_date = initial_date.replace(day=1)
    while current_date <= finish_date:
        yield current_date
        current_date += datetime.timedelta(days=32)
        current_date = current_date.replace(day=1)


@click.command()
@click.option('--email', prompt=True, help="Email used in your GuiaBolso accou"
                                           "nt")
@click.option('--password', prompt=True, hide_input=True)
@click.option('--year', prompt=True, type=int,
              help="Year from the transactions you are interested. It will be "
                   "used as the first year if LAST_YEAR is specified")
@click.option('--month', prompt=True, type=click.IntRange(1, 12),
              help="Month from the transactions you are interested. It will be"
                   " used as the first month if LAST_MONTH is specified")
@click.option('--last-year', type=int, default=None,
              help="If you specify last year it will be used as the last year "
                   "to get a range of years, starting in YEAR and ending in LA"
                   "ST_YEAR")
@click.option('--last-month', type=click.IntRange(1, 12), default=None,
              help="If you specify last month it will be used as the last mont"
                   "h to get a range of months, starting in MONTH and ending i"
                   "n LAST_MONTH")
@click.option('--excel', is_flag=True, help="Save transactions as xlsx instead"
                                            " of csv")
def main(email, password, year, month, last_year, last_month, excel):
    """Download GuiaBolso transactions in a csv format."""
    gb = GuiaBolso(email, password)

    initial_date = datetime.date(year, month, 1)
    finish_date = datetime.date(last_year or year, last_month or month, 1)

    for date in month_iterator(initial_date, finish_date):
        year = date.year
        month = date.month
        filename = "%i-%i" % (year, month)
        if excel:
            filename += '.xlsx'
            gb.xlsx_transactions(year, month, filename)
        else:
            filename += '.csv'
            gb.csv_transactions(year, month, filename)
        print filename

if __name__ == '__main__':
    main()
