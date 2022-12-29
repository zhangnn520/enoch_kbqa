# coding=utf-8
import os
import re
import csv
import json
import codecs
import pipetool
from functools import reduce
from tqdm import tqdm

base_dir = os.getcwd()


def load_data(filename):
    return pipetool.load(filename, file_format='jsons')


def read_text(path):
    with open(path, "r", encoding="utf-8") as reader:
        return [i.replace("\n", "") for i in reader.readlines()]


# 用户自定义词典

def find_chinese_word(string):
    string = string.strip()
    pattern = r"[\u4e00-\u9fa5]+"
    pat = re.compile(pattern)
    result = pat.findall(string)
    if result:
        return " ".join(result)
    else:
        return ""


def find_english_word(string):
    pattern = r"[a-zA-Z]+|（[a-zA-Z]+）"
    pat = re.compile(pattern)
    result = pat.findall(string.strip())
    return " ".join(result)


def find_index(string):
    pattern = r"[A-Z0-9,，]+"
    pat = re.compile(pattern)
    result_list = pat.findall(string)
    if result_list:
        return [result.replace(",", " ").replace("，", " ") for result in result_list][0]
    else:
        return ""


def get_string_index(string, string_one):
    index_num = -1
    index_list = []
    string_length = len(string_one)
    if string_length:
        b = string.count(string_one)
        for i in range(b):  # 查找所有的下标
            index_num = string.find(string_one, index_num + 1, len(string))
            index_list.append([str(index_num), str(index_num + string_length)])
    return index_list


def read_json(path, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as reader:
        return json.loads(reader.read())


def get_content(object_list, content_name="CONTENT"):
    return [content[f'{content_name}'] for content in object_list]


def write_text(write_path, content_line):
    with open(write_path, "w+", encoding="utf-8") as writer:
        for content in content_line:
            writer.write(content + "\n")


def write_text3(write_path, content_lines):
    with open(write_path, "w+", encoding="utf-8") as writer:
        for content_line in content_lines:
            for line in content_line:
                writer.write(line + "\n")
            writer.write("\n")


def write_json_by_line(write_path, content_line):
    with open(write_path, "w+", encoding="utf-8") as writer:
        for line in content_line:
            writer.write(json.dumps(line, ensure_ascii=False))
            writer.write("\n")


def get_maintain_clear_data(english_maintain, chinese_maintain):
    english_clear_data_list, chinses_clear_data_list = list(), list()
    for en in tqdm(english_maintain):
        for ch in chinese_maintain:
            if en['STATISTICS'] == ch['STATISTICS'] and en['HTML'].split("/")[-1] == ch['HTML'].split("/")[-1]:
                english_clear_data_list.append(en)
                chinses_clear_data_list.append(ch)
    try:
        assert len(english_clear_data_list) == len(chinses_clear_data_list)
    except Exception as e:
        print(e)
    return english_clear_data_list, chinses_clear_data_list


def fast_align_data(en_list, ch_list):
    en2ch_list = list()
    assert len(en_list) == len(ch_list)
    for num, ch_content in enumerate(ch_list):
        en_content = en_list[num]
        new_content = en_content + ' ||| ' + ch_content
        en2ch_list.append(new_content)
    return en2ch_list


def write_json(write_path, content_line):
    with open(write_path, "w+", encoding="utf-8") as writer:
        writer.write(json.dumps(content_line, ensure_ascii=False, indent=2))


def get_fast_align_data(en2chcontent, en2ch_align_content, word_align_result_path):
    """
    :param en2chcontent: 对齐原始预料
    :param en2ch_align_content: 对齐后产生的映射字典
    :param word_align_result_path: 写入对齐映射的文件目录
    :return: null
    """
    result_list = []
    for num, content in enumerate(en2chcontent):
        ens, chs = content.split("|||")
        id2en = {str(num): en for num, en in enumerate(ens.split(" "))}
        id2ch = {str(num): ch for num, ch in enumerate(chs.split(" "))}
        content_align = en2ch_align_content[num]
        en_word_mapping = [id2en[i.split("-")[0]] for i in content_align.replace("\n", "").split(" ")]
        ch_word_mapping = [id2ch[i.split("-")[1]] for i in content_align.replace("\n", "").split(" ")]
        result = dict(zip(en_word_mapping, ch_word_mapping))
        result_list.append(result)
    write_json(word_align_result_path, result_list)


def sub_word(string):
    pattern_one = u"\\(.*?\\)|\\（.*?）|\\[.*?]|-|“|”|``|''"
    result = re.sub(pattern_one, "", string)
    pattern_two = u" +"
    result = re.sub(pattern_two, " ", result)

    return result


def write_line_json(write_path, content_line):
    with open(write_path, "w+", encoding="utf-8") as writer:
        for line in content_line:
            writer.write(json.dumps({line: content_line[line]}, ensure_ascii=False))
            writer.write("\n")


def write_bio(write_path, content_line):
    with open(write_path, "w+", encoding="utf-8") as writer:
        for contents in content_line:
            for content in contents:
                writer.write(content + "\n")


def write_bio2(write_path, content_line):
    with open(write_path, "w+", encoding="utf-8") as writer:
        for contents in content_line:
            writer.writelines(contents)
            writer.write("\n")


def read_csv(read_path, model="utf-8"):
    content_list = list()
    with codecs.open(read_path, encoding=model) as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            content_list.append(row)
    return content_list


def delete_duplicate_elements(list_data):
    return reduce(lambda x, y: x if y in x else x + [y], [[], ] + list_data)


def write_ann_text(write_path, content_line):
    with open(write_path, "w+", encoding="utf-8") as writer:
        for content in content_line:
            writer.write(content + "\n")
