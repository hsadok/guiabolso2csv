# coding=utf-8
# main.py
# 2016, all rights reserved
import click as click
from guia_bolso import GuiaBolso


@click.command()
@click.option('--email', prompt=True, help="Email used in your GuiaBolso accou"
                                           "nt")
@click.option('--cpf', prompt=True, help="Your CPF (required by GuiaBolso)")
@click.option('--password', prompt=True, hide_input=True)
@click.option('--year', prompt=True, type=int,
              help="Year from the transactions you are interested. It will be "
                   "used as the first year if LAST-YEAR is specified")
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
def main(email, cpf, password, year, month, last_year, last_month):
    """Download GuiaBolso transactions in a csv format."""
    gb = GuiaBolso(email, cpf, password)

    if last_year is not None:
        year_range = range(year, last_year+1)
    else:
        year_range = [year]

    if last_month is not None:
        month_range = range(month, last_month+1)
    else:
        month_range = [month]

    for year in year_range:
        for month in month_range:
            filename = "%i-%i.csv" % (year, month)
            print filename
            gb.csv_transactions(year, month, filename)


if __name__ == '__main__':
    main()
