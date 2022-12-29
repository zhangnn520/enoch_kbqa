#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import datetime
from tools.tools import load_data
from tqdm import tqdm

from enoch_knowledge_qa.build_kg.neo4j_genration import Neo4jGraphCreate

url = "http://192.168.1.188:1120"
graph = Neo4jGraphCreate(url)
base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "enoch_data")
the_first_graph_file_path = os.path.join(base_dir, "data", "right_data.json")
if __name__ == "__main__":
    # todo 删除所有节点和关系
    # graph.delete_node_all()
    content_list = load_data(the_first_graph_file_path)
    for data in tqdm(content_list):
        text_content = data['text']
        # {44614【id】: ('部件单元'【label】, '发动机'【标注词语】), 44615: ('故障现象', '无法起动')}
        entity_dict = {i['id']: (i['label'], data['text'][i['start_offset']:i['end_offset']]) for i in data['entities']}
        # {'故障状态'【type】: (44615【from_id】, 44614【to_id】)}
        relation_dict = {i['type']: (i['from_id'], i['to_id']) for i in data['relations']}

        for j_key, j_value in relation_dict.items():
            create_node_relation_dict = {
                "head_node": {"node_property": {"name": entity_dict[j_value[0]][1]},
                              "label": [entity_dict[j_value[0]][0]]},
                "tail_node": {"node_property": {"name": entity_dict[j_value[1]][1]},
                              "label": [entity_dict[j_value[1]][0]]},
                "relation": {"properties": {"date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                             "label": j_key}}
            graph.main(create_node_relation_dict)
