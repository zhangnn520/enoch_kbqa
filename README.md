# 基于以诺行维修手册知识图谱的问答

# 代码工程目录
```
+--answer_search.py # 从eno4j数据库进行数据搜索
+--chatbot_graph.py # 对话机器人总入口
+--enoch_knowledge_qa # 以诺行数据及其数据写入代码
|      +--build_kg # 数据入库
|      |      +--create_enoch_neo4j.py
|      |      +--data_processor.py
|      |      +--get_request.py
|      |      +--neo4j_genration.py
|      |      +--故障知识图谱融合维修手册知识图谱.py
|      |      +--知识图谱融合至维修手册知识图谱.py
|      +--enoch_data
|      |      +--data
|      |      |      +--dim_be_maintain_frt.json
|      |      |      +--recreate_maintain_data_from_csv_file.py
|      |      |      +--right_data.json
|      |      |      +--修改版.csv
|      |      |      +--第一版知识图谱v1.0.json
|      |      |      +--经过结构化处理的维修手册子步骤.json
|      |      |      +--维修手册2-修改版_维修拆装数据copy.csv
|      |      |      +--维修手册子步骤.json
|      |      |      +--维修手册安装和拆卸子步骤.json
|      |      +--mid_data
|      |      |      +--maintain_sentence.txt
|      |      |      +--ner_result.txt
|      |      |      +--内容描述.txt
|      |      |      +--图谱关系类别.txt
|      |      |      +--安装和拆卸步骤.txt
|      |      |      +--性能表征.txt
|      |      |      +--故障现象.txt
|      |      |      +--故障设备.txt
|      |      |      +--维修手册安装和拆卸目录.txt
|      |      |      +--部件单元.txt
+--question_parser.py
+--README.md
+--requirements.txt
+--test_classification.py
+--tets.py
+--tools
|      +--tools.py
+--trie_tree.py
+--__init__.py

```



# 依赖

```python
py2neo版本：py2neo-2021.2.3
neo4j版本：neo4j-4.4.5
```

# 运行

在安装好neo4j之后，运行以下指令进行数据转化，在处理数据前需要首先启动flight_ner_flask服务，然后将维修手册中非结构化文本结构化处理：

```python
python data_processor.py
```

然后将处理好的数据集写入到知识图谱中：

```python
python create_enoch_neo4j.py
```

最后启动知识图谱服务

```
python chatbot_graph.py
```

# 参考

> https://github.com/liuhuanyong/QASystemOnMedicalKG

