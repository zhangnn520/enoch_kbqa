#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import datetime
import logging
from tqdm import tqdm
from tools.tools import read_json
from enoch_knowledge_qa.build_kg.neo4j_genration import Neo4jGraphCreate

base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "enoch_data")
url = "http://192.168.1.188:1120"
graph = Neo4jGraphCreate(url)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class GetNerMaintain:
    def __init__(self):
        self.file_path = os.path.join(base_dir, "data", "维修手册安装和拆卸子步骤.json")
        self.new_file_path = os.path.join(base_dir, "data", "经过结构化处理的维修手册子步骤.json")
        self.ner_file_path = os.path.join(base_dir, "data", "维修手册子步骤.json")

        self.origin_maintain_dict = read_json(self.file_path)
        self.ner_maintain_list = read_json(self.ner_file_path)

    def get_maintain_result(self):
        ner_maintain_dict = dict()
        for data in self.ner_maintain_list:
            new_data = {
                "content": data['raw_text'],
                "entities": data.get("entities"),
                # 'entity_spans': data.get('entity_spans')
            }
            ner_maintain_dict.update({data['raw_text']: new_data})
        return ner_maintain_dict

    def get_new_maintain_dict(self):
        new_maintain_dict = dict()
        ner_dict = self.get_maintain_result()
        install_and_uninstall_list = list()
        entities_list = list()
        for key, value in self.origin_maintain_dict.items():
            maintain_dict = dict()
            for sub_key, sub_value in value.items():
                install_and_uninstall_list.append({key: {sub_key: sub_value}})
                new_dict = dict()
                for _key, _value in sub_value.items():
                    try:
                        new_dict[_key] = ner_dict.get(_value)
                        entities_list.append({ner_dict.get(_value)['content']: ner_dict.get(_value)['entities']})
                    except Exception as e:
                        print(e, _key, _value)
                maintain_dict[sub_key] = new_dict
            new_maintain_dict[key] = maintain_dict
        # write_json(self.new_file_path, new_maintain_dict)
        return new_maintain_dict, install_and_uninstall_list, entities_list

    def __call__(self, *args, **kwargs):
        # 删除所有的节点和关系
        logger.info("删除所有的节点和关系！！")
        graph.delete_node_all()
        new_maintain_dict, install_and_uninstall_list, entities_list = self.get_new_maintain_dict()
        # 将实体类别诸如操作部件等写入知识图谱，首先建立entity节点
        logger.info("建立操作手册中安装和拆卸步骤节点")
        self.create_entities_node(entities_list)
        logger.info("写入安装和拆卸的子步骤及其关系")
        self.create_title_procedure_nodel_relation(new_maintain_dict)
        logger.info("建立子节点与安装拆卸步骤的关系！！！")
        self.procedure_processor(install_and_uninstall_list)
        logger.info("将建立子步骤节点并关联entity节点,以ner类别作为关系")
        self.create_entity_procedure(entities_list)

    @staticmethod
    def create_entity_procedure(entities_list):
        for data in tqdm(entities_list):
            for key, value in data.items():
                for i_key, i_value in value.items():
                    sub_install_dict = {
                        "head_node": {"node_property": {"name": key},
                                      "label": ("title", "install", "sub_procedure")},
                        "tail_node": {"node_property": {"name": i_value},
                                      "label": ["entity"]},
                        "relation": {"properties": {"name": i_key}, "label": "步骤ner"}}
                    graph.main(sub_install_dict)

    @staticmethod
    def create_list_node2(entity_list, _label: list):
        entity_list = list(set(entity_list))
        for node in tqdm(entity_list):
            node_relation_dict = {"head_node": {"node_property": {"name": "维修操作手册"},
                                                "label": ["node_grand"]},
                                  "tail_node": {"node_property": {"name": node},
                                                "label": ["entity"]},
                                  "relation": "手册目录"}

            graph.main(node_relation_dict)

    @staticmethod
    def create_entities_node(entities_list):
        entity_list = list()
        entity_label = "entity"
        for entity in entities_list:
            entity_list += [list(data.values()) for data in list(entity.values())][0]
        GetNerMaintain.create_list_node(entity_list, [entity_label])

    @staticmethod
    def create_list_node(entity_list, _label: list):
        entity_list = list(set(entity_list))
        for node in tqdm(entity_list):
            try:
                graph.create_entity_node(node, _label)
            except Exception as e:
                print(e, node)

    @staticmethod
    def create_title_procedure_nodel_relation(new_maintain_dict):
        # 建立label 为title的节点
        title_name_list = [j.replace(" ", "").replace("（拆卸和更换）", "") for j in list(new_maintain_dict.keys())]
        # 建立与title对应的安装和拆卸接节点
        for data in title_name_list:
            install_dict = {"head_node": {"node_property": {"name": data}, "label": ["title"]},
                            "tail_node": {"node_property": {"name": data + "&安装步骤"},
                                          "label": ("title", "install")},
                            "relation": {"properties": {"date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                                         "label": "安装步骤"}}
            uninstall_dict = {"head_node": {"node_property": {"name": data}, "label": ["title"]},
                              "tail_node": {"node_property": {"name": data + "&拆卸步骤"},
                                            "label": ("title", "uninstall")},
                              "relation": {
                                  "properties": {"date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                                  "label": "拆卸步骤"}}

            graph.main(install_dict)
            graph.main(uninstall_dict)

    @staticmethod
    def procedure_processor(procedure_list):
        for data in tqdm(procedure_list):
            for key, value in data.items():
                try:
                    head_node_name = key.replace(" ", "").replace("（拆卸和更换）", "")
                    if "安装部分" in value.keys():  # 安装部分处理
                        for i_key, i_value in value['安装部分'].items():
                            sub_install_dict = {
                                "head_node": {"node_property": {"name": head_node_name + "&安装步骤"},
                                              "label": ("title", "install")},
                                "tail_node": {"node_property": {"name": i_value},
                                              "label": ("title", "install", "sub_procedure")},
                                "relation": {"properties": {"name": i_key}, "label": "安装子步骤"}}
                            graph.main(sub_install_dict)

                    # 拆卸部分处理
                    else:
                        for j_key, j_value in value['拆卸部分'].items():
                            sub_install_dict = {
                                "head_node": {"node_property": {"name": head_node_name + "&拆卸步骤"},
                                              "label": ("title", "uninstall")},
                                "tail_node": {"node_property": {"name": j_value},
                                              "label": ("title", "uninstall", "sub_procedure")},
                                "relation": {"properties": {"name": j_key}, "label": "拆卸子步骤"}}
                            graph.main(sub_install_dict)

                except Exception as e:
                    print(e)


if __name__ == "__main__":
    get_ner_maintain = GetNerMaintain()
    get_ner_maintain()
