#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from py2neo import Graph, Node, Relationship, NodeMatcher


class Neo4jGraphCreate:
    def __init__(self, url):
        self.url = url
        self.auth_name = "neo4j"
        self.pass_words = "123456"
        self.graph = self.graph()

    def graph(self):
        graph = Graph(self.url, auth=(self.auth_name, self.pass_words))
        return graph

    def delete_node_all(self):
        # 删除已有的所有内容
        self.graph.delete_all()

    def main(self, node_dict):
        match_node1 = node_dict["head_node"]["node_property"]
        match_node2 = node_dict["tail_node"]["node_property"]
        relation = node_dict["relation"]["label"]
        relation_properties = node_dict["relation"]["properties"]
        node1_label = node_dict["head_node"]['label']
        node2_label = node_dict["tail_node"]['label']
        self.create_relation(match_node1, match_node2, relation, node1_label, node2_label, relation_properties)

    def create_entity_node(self, match_node_name: str, node_label: list):
        _sql = """MERGE (n:%s{name:"%s"})""" % (':'.join(node_label), match_node_name)
        self.graph.run(_sql)

    def create_node_sql(self, _sql):
        self.graph.run(_sql)

    def create_relation(self, match_node1, match_node2, relation, node1_label, node2_label, rel_properties):
        """自动创建节点与关系
            :param match_node1: 节点1属性
            :param match_node2: 节点2属性
            :param relation: 关系
            :param node1_label: 节点1的标签
            :param node2_label: 节点2的标签
            :param rel_properties: 关系属性
        """
        node_matcher = NodeMatcher(self.graph)
        node1 = node_matcher.match(**match_node1).first()
        # 自动创建node
        if not node1:
            if node1_label:
                node1 = Node(*node1_label, **match_node1)
            else:
                node1 = Node(**match_node1)
        node2 = node_matcher.match(**match_node2).first()
        if not node2:
            if node2_label:
                node2 = Node(*node2_label, **match_node2)
            else:
                node2 = Node(**match_node2)
        # 创建关系
        relation = Relationship(node1, relation, node2, **rel_properties)
        self.graph.create(relation)
