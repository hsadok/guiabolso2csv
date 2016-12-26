# coding=utf-8
# guia_bolso.py
# 2016, all rights reserved
import hashlib
import urllib
import uuid
import requests
import json
from collections import OrderedDict


def dict2url(d):
    return urllib.quote(json.dumps(d, separators=(',', ':')))


def get_month_count(year, month):
    return year * 12 + month - 1


class GuiaBolso(object):
    def __init__(self, email, cpf, password):
        self.email = email
        self.cpf = cpf
        self.password = password
        self.device_token = hashlib.md5(str(uuid.getnode())).hexdigest()
        self.session = requests.Session()
        self.login()

    def login(self):
        url = "https://www.guiabolso.com.br/comparador/api/v1/user/login"

        payload = """
        {
             "email":%s,
             "pwd":%s,
             "cpf":%s,
             "deviceToken":"%s",
             "appToken":"2.6.0",
             "origin":"https://www.guiabolso.com.br/comparador/#/login",
             "os":"(Macintosh; Intel Mac OS X 10_12_2)",
             "deviceName":"%s",
             "month":24191
        }""" % (json.dumps(self.email),
                json.dumps(self.password),
                json.dumps(self.cpf),
                self.device_token,
                self.device_token)

        headers = {
            'content-type': "application/json"
        }

        response = self.session.post(url, headers=headers, data=payload).json()

        if response['returnCode'] == 0:
            print response['error']['errorMessage']
            raise Exception(response['error'])

        print 'login 1/2'

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

        print 'login 2/2'

    def statement(self, year, month):
        month_count = get_month_count(year, month)
        url = "https://www.guiabolso.com.br/transactionsApi/list"

        model_dict = OrderedDict([
            ("month", month_count),
            ("showDuplicate", True)
        ])
        model = dict2url(model_dict)

        payload = {"model": model}
        response = self.session.get(url, params=payload)
        return response
