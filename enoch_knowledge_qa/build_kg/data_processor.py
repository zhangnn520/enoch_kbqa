#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# !/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import copy
import requests
from tqdm import tqdm
from tools.tools import read_csv, write_json, read_json

base_dir = os.path.dirname(__file__)
"""
将维修手册安装和拆卸的步骤，进行归类和解析，然后调用ner模型进行实体抽取，返回结构化数据
后续会采用这些数据进图谱生成
"""


class DataProcessor:
    def __init__(self):
        self.url = "http://localhost:12345/ner_server"  # 首先启动ner服务
        self.service_manual_path = os.path.join(base_dir, "data", "维修手册2-修改版_维修拆装数据copy.csv")
        self.new_manual_path = os.path.join(base_dir, "data", "维修手册安装和拆卸子步骤.json")
        self.model_predict_data_path = os.path.join(base_dir, "data", "维修手册子步骤.json")
        self.maintain_code_path = os.path.join(base_dir, "data", "dim_be_maintain_frt.json")
        self.code_dict = self.get_maintain_code()
        self.content_list = list()

    def get_maintain_code(self):
        maintain_code = read_json(self.maintain_code_path)
        code_dict = {i["FRT_CODE"]: i["PART_NAME"] for i in maintain_code["RECORDS"]}
        return code_dict

    @staticmethod
    def get_request(url, data_list):
        payload = {"content_list": [i for i in data_list if i]}
        response = requests.request("POST", url, json=payload)

        return response.json()

    @staticmethod
    def split_manual_maintain_content(data_list):
        content_data_dict = dict()
        for data in tqdm(data_list):
            if data['校正代码'] in content_data_dict.keys():
                temp_dict2 = dict()
                dict_value = copy.deepcopy(content_data_dict[data['校正代码']])
                temp_dict2["操作内容"] = data['操作内容']
                temp_dict2["整体序号"] = data['整体序号']
                temp_dict2["操作子内容"] = data['操作子内容']
                dict_value.append(temp_dict2)
                content_data_dict[data['校正代码']] = dict_value
            else:
                temp_dict1 = dict()
                temp_dict1["操作内容"] = data['操作内容']
                temp_dict1["整体序号"] = data['整体序号']
                temp_dict1["操作子内容"] = data['操作子内容']
                content_data_dict[data['校正代码']] = [temp_dict1]
        return content_data_dict

    def split_install_and_removal_step(self, data_dict):
        new_dict_data = dict()

        for key, values in data_dict.items():
            try:
                flag = False
                install_list, removal_list = list(), list()
                for value in values:
                    if value['整体序号'] == "1":
                        if values.index(value) == 0:  # 第一次出现整体序号为1的情况
                            flag = True
                            if value['操作子内容']:
                                if value['操作子内容']:
                                    install_list.append(value['操作子内容'])
                            else:
                                if value['操作内容']:
                                    install_list.append(value['操作内容'])
                        else:  # 第二次出现整体序号的情况
                            flag = False
                            if value['操作子内容']:
                                if value['操作子内容']:
                                    removal_list.append(value['操作子内容'])
                            else:
                                if value['操作内容']:
                                    removal_list.append(value['操作内容'])
                    else:
                        if flag:  # 第一次出现整体序号为1时，逐步加入后续步骤的内容
                            if value['操作子内容']:
                                if install_list[-1] != value['操作子内容']:
                                    if value['操作子内容']:
                                        install_list.append(value['操作子内容'])
                            else:
                                if install_list[-1] != value['操作内容']:
                                    if value['操作内容']:
                                        install_list.append(value['操作内容'])
                        else:  # 第二次出现整体序号为1时，逐步加入后续步骤的内容
                            if value['操作子内容']:
                                if install_list[-1] != value['操作子内容']:
                                    if value['操作子内容']:
                                        removal_list.append(value['操作子内容'])
                            else:
                                if install_list[-1] != value['操作内容']:
                                    if value['操作内容']:
                                        removal_list.append(value['操作内容'])
                self.content_list += install_list
                self.content_list += removal_list
                new_dict_data[self.code_dict[key]] = {
                    "安装部分": {"安装子步骤" + str(num + 1): i for num, i in enumerate(install_list)},
                    "拆卸部分": {"拆卸子步骤" + str(num + 1): j for num, j in enumerate(removal_list)}}
            except Exception as e:
                print(f"{e}对应code缺少对应的操作名称，需要确认{key}")  # 哪些code没有对应拆卸安装步骤
        self.content_list = list(set(self.content_list))
        return new_dict_data, self.content_list

    def __call__(self, *args, **kwargs):
        content_list = [dict(data) for data in read_csv(self.service_manual_path, model="gbk")]
        maintain_data = self.split_manual_maintain_content(content_list)
        new_data, content_list = self.split_install_and_removal_step(maintain_data)
        write_json(self.new_manual_path, new_data)
        new_content_list = self.get_request(self.url, content_list)
        write_json(self.model_predict_data_path, new_content_list)


if __name__ == "__main__":
    data_processor = DataProcessor()
    data_processor()
