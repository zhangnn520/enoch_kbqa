def build_entity_dict(parser_args):
    node_name_list = list()
    question_type = parser_args['question_types']
    for key, value in parser_args['args'].items():
        node_name_list.append(key)
    return question_type, node_name_list


class QuestionPaser:
    # 构建实体节点
    @staticmethod
    def parser_main(res_classify):
        temp_dict = dict()
        question_type, node_list = build_entity_dict(res_classify)
        temp_dict['question_type'] = question_type
        temp_dict['head_node'] = node_list[0]
        temp_dict['node_relation'] = node_list[1]
        # 对传入步骤的ner结果进行查询
        if question_type == ['查看操作步骤ner结果']:

            _sql = """MATCH (n:`title`) where n.name=~".*%s.*" 
            MATCH p=(n)-[jx:`步骤ner`{name:"%s"}]->(m) return m.name""" \
                   % (node_list[0], node_list[1])
            temp_dict['_sql'] = _sql
            return temp_dict
        #  查看安装和拆卸步骤
        elif question_type == ['查看安装和拆卸步骤']:
            _sql = """MATCH (n:`title`) where n.name=~".*%s.*"\nMATCH p=(n)-[jx:`%s`]->(m) return m.name""" \
                   % (node_list[0], node_list[1])
            temp_dict['_sql'] = _sql
            return temp_dict
        # 查看安装和拆卸的子步骤
        elif question_type == ['查看安装和拆卸子步骤']:
            _sql = """MATCH (n:`title`) where n.name=~".*%s.*"\nMATCH p=(n)-[jx:`%s`]->(m) return m.name""" \
                   % (node_list[0], node_list[1])
            temp_dict['_sql'] = _sql
            return temp_dict
        # 查看故障原因
        elif question_type == ['故障原因']:
            _sql = """MATCH (n:`内容描述`) where n.name=~".*%s.*"\nMATCH p=(n)-[jx:`%s`]->(m) return m.name""" \
                   % (node_list[0], node_list[1])
            temp_dict['_sql'] = _sql
            return temp_dict
        # 查看'改进方案', "故障原因", "故障状态", "故障条件", "组成"都属于故障知识图谱类别
        elif question_type == ['故障知识图谱类别']:
            _sql = """MATCH (n) where n.name=~".*%s.*"\nMATCH p=(n)-[jx:`%s`]->(m) return m.name""" \
                   % (node_list[0], node_list[1])
            temp_dict['_sql'] = _sql
            return temp_dict


if __name__ == '__main__':
    args = {'args': {'起动后有尖叫声/方向打死有尖叫声': ['fault_phenomenon'],
                     '改进方案': ['fault_equipment']}, 'question_types': ['故障知识图谱类别']}

    handler = QuestionPaser()
    sql = handler.parser_main(args)
    print(sql)
