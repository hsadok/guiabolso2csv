# coding=utf-8
# main.py
# 2016, all rights reserved
import click as click
from guia_bolso import GuiaBolso


@click.command()
@click.option('--email', prompt=True)
@click.option('--cpf', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def main(email, cpf, password):
    gb = GuiaBolso(email, cpf, password)
    statement = gb.statement(2016, 12)
    print statement.json()


if __name__ == '__main__':
    main()
