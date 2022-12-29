from test_classification import *
from question_parser import *
from answer_search import *


class ChatBotGraph:
    def __init__(self):
        self.classifier = MyQuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        global answer
        answer = '没能理解您的问题，请问的标准!!'
        try:
            res_classify = self.classifier.classify(sent)
            if not res_classify:
                return answer
            res_sql = self.parser.parser_main(res_classify)
            final_answers = self.searcher.search_main(res_sql)
            if not final_answers:
                return answer
            else:
                return "".join(final_answers)
        except Exception as e:
            print(e)
            return answer


if __name__ == '__main__':
    handler = ChatBotGraph()
    while True:
        question = input('请输入咨询内容:')
        answer = handler.chat_main(question)
        print('enoch客服机器人:', answer)
