#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import csv
from tqdm import tqdm
from tools.tools import read_csv, read_json

base_dir = os.path.dirname(__file__)


def write_csv(path, big_data, head_list):
    with open(path, 'w+', encoding='utf-8', newline="") as f:
        csv_write = csv.writer(f)
        csv_write.writerow(head_list)
        for data in tqdm(big_data):
            # ["校正代码", "整体序号", "操作内容", "操作子内容"]
            csv_write.writerow([data["校正代码"], data["整体序号"], data["操作内容"], data["操作子内容"]])


def get_maintain_code(maintain_code_path):
    maintain_code = read_json(maintain_code_path)
    code_dict = {i["FRT_CODE"]: i["PART_NAME"] for i in maintain_code["RECORDS"]}
    return code_dict


file_name_list = os.listdir(os.path.join(base_dir, "维修手册生成"))
code_dict = get_maintain_code(os.path.join(base_dir, "dim_be_maintain_frt.json"))
csv_file_path = os.path.join(base_dir, "修改版.csv")
all_content_list = list()
for file_name in file_name_list:

    file_path = os.path.join(os.path.join(base_dir, "维修手册生成"), file_name)
    content_list = [dict(data) for data in read_csv(file_path)]
    for num, data_dict in enumerate(content_list):
        try:
            temp_dict = dict()
            temp_dict["校正代码"] = data_dict["校正代码"]
            temp_dict["操作内容"] = data_dict["操作内容"]
            temp_dict["整体序号"] = data_dict["整体序号"]
            temp_dict["操作子内容"] = data_dict["操作子内容"]
            all_content_list.append(temp_dict)
        except Exception as e:
            print(e, file_path, num)
header_list = ["校正代码", "整体序号", "操作内容", "操作子内容"]
write_csv(csv_file_path, all_content_list, header_list)
