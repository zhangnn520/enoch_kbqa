from py2neo import Graph


class AnswerSearcher:
    def __init__(self):
        self.g = Graph("http://192.168.1.188:1120", auth=("neo4j", "123456"))
        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''

    def search_main(self, sql_object):
        question_type = sql_object['question_type']
        head_node = sql_object['head_node']
        node_relation = sql_object['node_relation']
        _sql = sql_object['_sql']
        graph_data = self.g.run(_sql).data()
        result_data = self.answer_prettify(question_type, head_node, node_relation, graph_data)
        return result_data

    def answer_prettify(self, question_type, head_node, node_relation, graph_data):
        if not graph_data:  # 无答案
            return ''
        else:
            desc = [i['m.name'] for i in graph_data]
        if question_type == ['故障知识图谱类别']:
            answer = "{0}的{1}是：{2}".format(head_node, node_relation, '；'.join(list(set(desc))[:self.num_limit]))
            return answer
        elif question_type == ['查看操作步骤ner结果']:
            answer = "{0}的{1}是：{2}".format(head_node, node_relation, '；'.join(list(set(desc))[:self.num_limit]))
            return answer
        elif question_type == ['查看安装和拆卸步骤']:
            answer = "{0}的{1}是：{2}".format(head_node, node_relation, '；'.join(list(set(desc))[:self.num_limit]))
            return answer
        elif question_type == ['查看安装和拆卸子步骤']:
            answer = "{0}的{1}是：{2}".format(head_node, node_relation, '；'.join(list(set(desc))[:self.num_limit]))
            return answer
        elif question_type == ['故障知识图谱类别']:
            answer = "{0}的{1}是：{2}".format(head_node, node_relation, '；'.join(list(set(desc))[:self.num_limit]))
            return answer



if __name__ == '__main__':
    sql_dict1 = {'question_type': ['故障知识图谱类别'],
                 'head_node': '起动后有尖叫声/方向打死有尖叫声',
                 'node_relation': '改进方案',
                 '_sql': 'MATCH (n) where n.name=~".*起动后有尖叫声/方向打死有尖叫声.*"'
                         'MATCH p=(n)<-[jx:`改进方案`]-(m) return m.name'}
    sql_dict2 = {'question_type': ['查看操作步骤ner结果'],
                 'head_node': '将驾驶位和副驾位座椅移回原位',
                 'node_relation': '一般动作',
                 '_sql': 'MATCH (n:`title`) where n.name=~".*将驾驶位和副驾位座椅移回原位.*"'
                         'MATCH p=(n)-[jx:`步骤ner`{name:"一般动作"}]->(m) return m.name'}
    sql_dict3 = {'question_type': ['查看安装和拆卸步骤'],
                 'head_node': '盖板-后悬架-LH', 'node_relation': '安装步骤',
                 '_sql': 'MATCH (n:`title`) where n.name=~".*盖板-后悬架-LH.*"'
                         'MATCH p=(n)-[jx:`安装步骤`]->(m) return m.name'}
    sql_dict4 = {'question_type': ['查看安装和拆卸子步骤'],
                'head_node': '热交换器-后驱动单元&拆卸步骤',
                'node_relation': '拆卸子步骤',
                '_sql': 'MATCH (n:`title`) where n.name=~".*热交换器-后驱动单元&拆卸步骤.*"'
                        'MATCH p=(n)-[jx:`拆卸子步骤`]->(m) return m.name'}
    sql_dict = {'question_type': ['故障知识图谱类别'],
                'head_node': '起动后有尖叫声/方向打死有尖叫声',
                'node_relation': '故障状态',
                '_sql': 'MATCH (n) where n.name=~".*起动后有尖叫声/方向打死有尖叫声.*"\nMATCH p=(n)-[jx:`故障状态`]->(m) return m.name'}

    searcher = AnswerSearcher()
    final_answer = searcher.search_main(sql_dict)
    print(final_answer)
