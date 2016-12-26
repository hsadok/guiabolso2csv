# coding=utf-8
# main.py
# 2016, all rights reserved
import click as click
from guia_bolso import GuiaBolso


@click.command()
@click.option('--email', prompt=True)
@click.option('--cpf', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--year', prompt=True, type=int)
@click.option('--month', prompt=True, type=int)
@click.option('--filename', prompt=True)
def main(email, cpf, password, year, month, filename):
    gb = GuiaBolso(email, cpf, password)
    gb.csv_transactions(year, month, filename)


if __name__ == '__main__':
    main()
