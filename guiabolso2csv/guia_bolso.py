# coding=utf-8
# guia_bolso.py
# 2016, all rights reserved
import datetime
import unicodecsv as csv
import re
import hashlib
import uuid
import requests
import json
import warnings
from collections import OrderedDict
import openpyxl

# handle urllib quote import in Py2 and Py3
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


def dict2url(d):
    return quote(json.dumps(d, separators=(',', ':')))


def get_month_count(year=None, month=None):
    today = datetime.date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    return year * 12 + month - 1


# use this to get json objects within a js file (or inline script in HTML)
def get_js_objects(complete_js, objects_list):
    js_objects = {}

    for obj in objects_list:
        str_match = re.search(obj + " *= *.+", complete_js).group()
        key, value = re.split(' *= *', str_match)
        js_objects[key] = json.loads(value[:-1])

    return dict(js_objects)


class GuiaBolso(object):
    def __init__(self, email, password):
        self.token = ""
        self.email = email
        self.password = password
        hardware_address = str(uuid.getnode()).encode('utf-8')
        self.device_token = hashlib.md5(hardware_address).hexdigest()
        self.session = requests.Session()
        self.token = self.login()
        basic_info = self.get_basic_info()
        self.categories = basic_info["categoryTypes"]
        # self.months = basic_info["GB.months"]
        self.statements = basic_info["accounts"]
        self.fieldnames = [
            u'id', u'label', u'description', u'date', u'account', u'category',
            u'subcategory', u'duplicated', u'currency', u'value', u'deleted'
        ]
        self.category_resolver = {}
        for categ in self.categories:
            for sub_categ in categ['categories']:
                self.category_resolver[sub_categ['id']] = \
                    (categ['name'], sub_categ['name'])

        self.account_resolver = {}
        for account in self.statements:
            for sub_account in account['statements']:
                self.account_resolver[sub_account['id']] = sub_account['name']

    def login(self):
        url = "https://www.guiabolso.com.br/API/events/others/"

        payload = """
        {
             "payload":{"email":%s,
                        "userPlatform":"GuiaBolso",
                        "pwd":%s,
                        "deviceToken":"%s",
                        "pnToken":"",
                        "origin":"iOS",
                        "appVersion":"7.1.2",
                        "deviceName":"%s"},
             "metadata":{"origin":"iOS",
                         "appVersion":"7.1.2"},
             "version":"6",
             "flowId":"",
             "id":"",
             "name":"users:login"
        }""" % (json.dumps(self.email),
                json.dumps(self.password),
                self.device_token,
                self.device_token)

        headers = {
            'content-type': "application/json"
        }

        self.session.headers.update({
            'User-Agent': 'Guiabolso/235 CFNetwork/893.14.2 Darwin/17.3.0'
        })

        response = self.session.post(url, headers=headers, data=payload).json()

        if response['name'] != "users:login:response":
            print(response['name'])
            raise Exception(response['payload']['code'])

        return response['auth']['token']

    def get_basic_info(self):
        url = "https://www.guiabolso.com.br/comparador/v2/events/"

        headers = {
            'content-type': "application/json"
        }

        payload = """
        {
            "name":"rawData:info",
            "version":"6",
            "payload":{"userPlatform":"GUIABOLSO",
                       "appToken":"1.1.0",
                       "os":"Win32"},
            "flowId":"",
            "id":"",
            "auth":{"token":"Bearer %s",
                    "sessionToken":"%s",
                    "x-sid":"",
                    "x-tid":""},
            "metadata":{"origin":"web",
                        "appVersion":"1.0.0",
                        "createdAt":""},
            "identity":{}
        }""" % (self.token,
                self.token)

        response = self.session.post(url, headers=headers, data=payload).json()

        # if response['name'] == "rawData:info:response":
        #     print("basicInfo OK")
        d = {}
        d['categoryTypes'] = response['payload']['categoryTypes']
        d['accounts'] = response['payload']['accounts']
        return dict(d)

    def json_transactions(self, year, month):
        month_count = get_month_count(year, month)
        url = "https://www.guiabolso.com.br/comparador/v2/events/"

        headers = {
            'content-type': "application/json"
        }

        payload = """
        {
             "name":"users:summary:month",
             "version":"1",
             "payload":{"userPlatform":"GUIABOLSO",
                        "appToken":"1.1.0",
                        "os":"Win32",
                        "monthCode":%i},
             "flowId":"",
             "id":"",
             "auth":{"token":"Bearer %s",
                     "sessionToken":"%s",
                     "x-sid":"",
                     "x-tid":""},
             "metadata":{"origin":"web",
                         "appVersion":"1.0.0",
                         "createdAt":"2020-04-25T20:20:05.552Z"},
             "identity":{}
        }""" % (month_count,
                self.token,
                self.token)

        response = self.session.post(url, headers=headers, data=payload)
        # if response.json()['name'] == "users:summary:month:response":
        #     print("Transaction OK")

        return response

    def transactions(self, year, month):
        transactions_new = []
        transactions = self.json_transactions(year, month).json()
        statements = transactions['payload']['userMonthHistory']['statements']
        for statement in statements:
            for t in statement['transactions']:
                cat_id = t['categoryId']
                t['category'], t['subcategory'] = self.category_resolver[cat_id]
                t['account'] = self.account_resolver.get(
                    t['statementId'], t['statementId'])
                unwanted_keys = set(t) - set(self.fieldnames)

                for k in unwanted_keys:
                    del t[k]
                transactions_new.append(t)

        return transactions_new

    def csv_transactions(self, year, month, file_name):
        transactions = self.transactions(year, month)

        if len(transactions) == 0:
            warnings.warn('No transactions for the period ({}-{})'.format(
                year, month))
            return

        with open(file_name, 'wb') as f:
            csv_writer = csv.DictWriter(f, fieldnames=self.fieldnames,
                                        encoding='utf-8-sig')  # add BOM to csv
            csv_writer.writeheader()
            csv_writer.writerows(transactions)

    def xlsx_transactions(self, year, month, file_name):
        transactions = self.transactions(year, month)

        if len(transactions) == 0:
            warnings.warn('No transactions for the period ({}-{})'.format(
                year, month))
            return

        wb = openpyxl.Workbook()
        ws = wb.active

        ws.append(self.fieldnames)

        for trans in transactions:
            if u'date' in trans:
                trans[u'date'] = datetime.datetime.fromtimestamp(
                    trans[u'date']/1000).date()
            row = [trans[k] for k in self.fieldnames]
            ws.append(row)

        wb.save(file_name)
