# coding=utf-8
# guia_bolso.py
# 2016, all rights reserved
import datetime
import unicodecsv as csv
import re
import hashlib
import urllib
import uuid
import requests
import json
from collections import OrderedDict
import openpyxl


def dict2url(d):
    return urllib.quote(json.dumps(d, separators=(',', ':')))


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
        self.email = email
        self.password = password
        self.device_token = hashlib.md5(str(uuid.getnode())).hexdigest()
        self.session = requests.Session()
        self.login()
        basic_info = self.get_basic_info()
        self.categories = basic_info["GB.categories"]
        self.months = basic_info["GB.months"]
        self.statements = basic_info["GB.statements"]
        self.fieldnames = [u'name', u'label', u'date', u'account', u'category',
                           u'subcategory', u'duplicated', u'currency',
                           u'value', u'deleted']

        self.category_resolver = {}
        for categ in self.categories:
            for sub_categ in categ['categories']:
                self.category_resolver[sub_categ['id']] = \
                    (categ['name'], sub_categ['name'])

        self.account_resolver = {}
        for account in self.statements:
            for sub_account in account['accounts']:
                self.account_resolver[sub_account['id']] = sub_account['name']

    def login(self):
        url = "https://www.guiabolso.com.br/comparador/api/v1/user/login"

        payload = """
        {
             "email":%s,
             "pwd":%s,
             "deviceToken":"%s",
             "appToken":"2.6.0",
             "origin":"https://www.guiabolso.com.br/comparador/#/login",
             "os":"(NOPE)",
             "deviceName":"%s",
             "month":%i
        }""" % (json.dumps(self.email),
                json.dumps(self.password),
                self.device_token,
                self.device_token,
                get_month_count())

        headers = {
            'content-type': "application/json"
        }

        response = self.session.post(url, headers=headers, data=payload).json()

        if response['returnCode'] == 0:
            print response['error']['errorMessage']
            raise Exception(response['error'])

        url = "https://www.guiabolso.com.br/access/login"
        payload_dict = OrderedDict([
            ("deviceToken", self.device_token),
            ("email", self.email),
            ("pwd", self.password)
        ])
        payload = "model=" + dict2url(payload_dict)

        mp_gb_dict = OrderedDict([
            ("distinct_id", self.email),
            ("$initial_referrer", "$direct"),
            ("$initial_referring_domain", "$direct")
        ])
        cookie = "mp_gb=%s; mp_mixpanel__c=1" % dict2url(mp_gb_dict)
        headers = {
            'cookie': cookie,
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8"
        }

        response = self.session.post(url, headers=headers, data=payload).json()

        if response['success'] != 1:
            print response['message']
            raise Exception(response['message'])

    def get_basic_info(self):
        url = "https://www.guiabolso.com.br/extrato"
        response = self.session.get(url)
        d = get_js_objects(response.text,
                           ["GB.categories", "GB.months", "GB.statements"])
        return d

    def json_transactions(self, year, month):
        month_count = get_month_count(year, month)
        url = "https://www.guiabolso.com.br/transactionsApi/list"

        model_dict = OrderedDict([
            ("month", month_count),
            ("showDuplicate", True)
        ])
        model = dict2url(model_dict)

        response = self.session.get(url + '?model=' + model)
        return response

    def transactions(self, year, month):
        transactions = self.json_transactions(year, month).json()

        for t in transactions:
            cat_id = t['category']['id']
            t['category'], t['subcategory'] = self.category_resolver[cat_id]

            # When the account name cannot be resolved, we use the id...
            t['account'] = self.account_resolver.get(
                t['statementId'], t['statementId']
            )
            unwanted_keys = set(t) - set(self.fieldnames)
            for k in unwanted_keys:
                del t[k]

        return transactions

    def csv_transactions(self, year, month, file_name):
        transactions = self.transactions(year, month)

        with open(file_name, 'wb') as f:
            csv_writer = csv.DictWriter(f, fieldnames=self.fieldnames,
                                        encoding='utf-8-sig')  # add BOM to csv
            csv_writer.writeheader()
            csv_writer.writerows(transactions)

    def xlsx_transactions(self, year, month, file_name):
        transactions = self.transactions(year, month)
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
