#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from tools.tools import read_json
from tqdm import tqdm
from enoch_knowledge_qa.build_kg.neo4j_genration import Neo4jGraphCreate

url = "http://192.168.1.188:1124"
graph = Neo4jGraphCreate(url)
base_dir = os.path.dirname(__file__)
the_first_graph_file_path = os.path.join(base_dir, "data", "第一版知识图谱v1.0.json")

if __name__ == "__main__":
    content_list = read_json(the_first_graph_file_path, encoding="utf-8")
    # todo 删除neo4j中节点和关系
    graph.delete_node_all()
    for data in tqdm(content_list):

        try:
            n_node_label = data['n']['labels']
            n_node_name = data['n']['properties']['name']
            n_node_properties_dict = data['n']['properties']
            m_node_label = data['m']['labels']
            m_node_name = data['m']['properties']['name']
            m_node_properties_dict = data['m']['properties']
            relation_name = data['jx']['type']
            # 添加n节点
            for n_key, n_value in n_node_properties_dict.items():
                if n_key != "name":  # 增加node属性
                    n_sql = """MERGE (n:%s{name:"%s"}) set n.%s='%s'""" % (
                        ':'.join(n_node_label), n_node_name, n_key, n_value)
                else:  # 增加节点name
                    n_sql = """MERGE (n:%s{name:"%s"})""" % (':'.join(n_node_label), n_node_name)
                graph.create_node_sql(n_sql)
            # 添加m节点
            for m_key, m_value in m_node_properties_dict.items():
                if m_key != "name":  # 增加node属性
                    m_sql = """MERGE (m:%s{name:"%s"}) set m.%s='%s'""" % (
                        ':'.join(m_node_label), m_node_name, m_key, m_value)
                else:  # 增加节点name
                    m_sql = """MERGE (m:%s{name:"%s"})""" % (':'.join(m_node_label), m_node_name)
                graph.create_node_sql(m_sql)
            # 添加n和m的关系
            create_relation_sql = """MATCH (n:%s{name:"%s"})\n
                                     MATCH (m:%s{name:"%s"})\n
                                     CREATE(n)-[jx:%s]->(m) """ % \
                                  (':'.join(n_node_label), n_node_name, ':'.join(m_node_label), m_node_name,
                                   relation_name)
            graph.create_node_sql(create_relation_sql)
        except Exception as e:
            print(e, data['m']['properties'])
