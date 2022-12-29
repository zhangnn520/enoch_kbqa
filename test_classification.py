#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import logging
from trie_tree import LexiconNER

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "enoch_knowledge_qa/enoch_data"))


def check_words(wds, sent):
    for wd in wds:
        if wd in sent:
            return True
    return False


class MyQuestionClassifier:
    def __init__(self):
        # 维修手册中安装和拆卸操作步骤内容步骤
        self.maintain_sentence_path = os.path.join(base_dir, 'mid_data/maintain_sentence.txt')
        # 知识图谱中所有ner名称类别
        self.ner_result_path = os.path.join(base_dir, 'mid_data/ner_result.txt')
        # 维修手册安装和拆卸目录
        self.install_uninstall_maintain_path = os.path.join(base_dir, "mid_data", "维修手册安装和拆卸目录.txt")
        # 知识图谱中所有的内容描述
        self.content_description_path = os.path.join(base_dir, "mid_data", "内容描述.txt")
        # 故障知识图谱所有的故障现象
        self.fault_phenomenon_path = os.path.join(base_dir, "mid_data", "故障现象.txt")
        # 维修手册知识图谱安装和拆卸
        self.manual_install_or_uninstall_path = os.path.join(base_dir, "mid_data", "安装和拆卸步骤.txt")
        # todo 加载特征词
        entity_dicts = {
            "maintain_sentence": [i.strip() for i in open(self.maintain_sentence_path, encoding="utf-8") if i.strip()],
            "install_uninstall_maintain": [i.strip() for i in open(self.install_uninstall_maintain_path,
                                                                   encoding="utf-8") if i.strip()],
            "manual_install_or_uninstall": [i.strip() for i in open(self.manual_install_or_uninstall_path,
                                                                    encoding="utf-8") if i.strip()],

            "content_description": [i.strip() for i in open(self.content_description_path,
                                                            encoding="utf-8") if i.strip()],
            "fault_phenomenon": [i.strip() for i in open(self.fault_phenomenon_path, encoding="utf-8") if i.strip()]

        }
        # 获取所有的特征词，并形成词典
        # 1、查询子步骤的ner结果
        self.ner_result_qwds = [i.strip() for i in open(self.ner_result_path, encoding="utf-8") if i.strip()]
        entity_dicts.update({"ner_result": self.ner_result_qwds})
        # 2、查询安装和拆卸步骤
        self.install_or_uninstall_maintain_qwds = ["拆卸步骤", "安装步骤"]
        entity_dicts.update({"install_or_uninstall_maintain": self.install_or_uninstall_maintain_qwds})
        # 3、 查询安装和拆卸子步骤
        self.manual_install_or_uninstall_qwds = ["拆卸子步骤", "安装子步骤"]
        entity_dicts.update({"manual_install_or_uninstall": self.manual_install_or_uninstall_qwds})
        # 4、查看故障现象
        self.fault_equipment_qwds = ['改进方案', "故障原因", "故障状态", "故障条件", "组成"]
        entity_dicts.update({"fault_equipment": self.fault_equipment_qwds})

        print('model init finished ......')
        self.lexicon_ner = LexiconNER(entity_dicts)

    # 问题列表判别函数
    def classify(self, question):
        data = dict()
        entity_dict = dict()
        types = set()
        entities = self.lexicon_ner(question)
        # 收集问句当中所涉及到的实体类型
        for entity in entities:
            types.add(entity['type'])
            if entity['text'] not in entity_dict:
                entity_dict[entity['text']] = [entity['type']]

            else:
                if entity['type'] not in entity_dict[entity['text']]:
                    entity_dict[entity['text']].append(entity['type'])

        types = list(types)
        data['args'] = entity_dict
        question_types = []

        # 查询操作步骤的ner结果
        if check_words(self.ner_result_qwds, question) and "maintain_sentence" in types:
            question_type = '查看操作步骤ner结果'
            question_types.append(question_type)

        # 查询安装和拆卸子步骤
        if check_words(self.manual_install_or_uninstall_qwds, question) and "manual_install_or_uninstall" in types:
            question_type = '查看安装和拆卸子步骤'
            question_types.append(question_type)

        # 查询安装和拆卸步骤
        if check_words(self.install_or_uninstall_maintain_qwds,
                       question) and "install_uninstall_maintain" in types:
            question_type = '查看安装和拆卸步骤'
            question_types.append(question_type)
        # # 查看故障现象
        # if check_words(self.fault_equipment_qwds, question) and "fault_phenomenon" in types:
        #     question_type = '故障现象'
        #     question_types.append(question_type)
        # 查看故障原因
        if check_words(self.fault_equipment_qwds, question) and "fault_equipment" in types:
            question_type = '故障知识图谱类别'
            question_types.append(question_type)
        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types
        if question_types == ['查看安装和拆卸子步骤', '查看安装和拆卸步骤']:
            new_data = {'args': {"&".join(list(data['args'].keys())[:-1]): list(data['args'].values())[0],
                                 list(data['args'].keys())[-1]: ['manual_install_or_uninstall']},
                        'question_types': ['查看安装和拆卸子步骤']}

            return new_data
        else:
            return data


if __name__ == '__main__':
    handler = MyQuestionClassifier()
    # while True:
    #     question = input('input an question:')
    #     data = handler.classify(question)
    #     print(data)

    # todo 示例如下：
    # question = "'将驾驶位和副驾位座椅移回原位'的一般动作"
    # question = "盖板-后悬架-LH的安装步骤"
    # question = "热交换器-后驱动单元&拆卸步骤的拆卸子步骤"
    # question = "DTC54控制模块的电源线路（蓄电池电压低）的故障原因"
    question = "起动后有尖叫声/方向打死有尖叫声的故障状态"
    # question = "冒黑烟的改进方案"
    data = handler.classify(question)
    print(data)
