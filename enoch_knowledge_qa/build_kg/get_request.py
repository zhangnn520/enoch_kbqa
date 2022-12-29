#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import requests


def get_request(data_list):
    url = "http://localhost:12345/ner_server"
    payload = {"content_list": data_list}
    response = requests.request("POST", url, json=payload)

    return response.json()
