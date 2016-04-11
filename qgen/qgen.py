import yaml
from importlib import import_module
from built_in_functions import built_in_functions as functions
from exceptions import InvalidConfigException
import generators.moodle_xml_builder as mxb


# TODO - convert to moodle xml
class Question(object):
    COMPULSORY_CONFIGS = ['type', 'title', 'answer', 'body']

    """Class to model a generate questions"""

    def __init__(self, configuration, question_count=0):
        self.question_params = {}
        self.add_config(configuration)
        self.question_count = question_count
        self.add_imports(configuration)
        self.build_question_params(configuration['params'])
        self.params_cache = self.question_params

    def add_config(self, config):
        if self.check_config(config):
            self.add_compulsory_config(config)            
        self.distractors = config['distractor'] if 'distractor' in config else {}
        self.correct_feedback = config['correct_feedback'] if 'correct_feedback' in config else {}
        self.incorrect_feedback = config['incorrect_feedback'] if 'incorrect_feedback' in config else {}
        self.correct_answer_weight = config['correct_answer_weight'] if 'correct_answer_weight' in config else {}
        self.incorrect_answer_weight = config['incorrect_answer_weight'] if 'incorrect_answer_weight' in config else{}

    def check_config(self, config):
        for name in Question.COMPULSORY_CONFIGS:            
            if name not in config:
                raise InvalidConfigException(name + " is missing from the configuration.")
        return True

    def add_compulsory_config(self, config):
        self.type = config['type']
        self.title = config['title']
        self.answers = config['answer']
        self.body = config['body']

    @staticmethod
    def add_imports(data):
        """Imports any external functions specified"""
        if 'imports' in data:
            imports = data['imports']
            for source in imports:
                try:
                    module = import_module(source)
                    for name, value in module.__dict__.iteritems():  # iterate through the module's attributes
                        if callable(value):  # check if callable for functions
                            functions[name] = value
                except AttributeError as e:
                    print e

    def build_question_params(self, params):
        """Binds the parameters to there actual values"""
        list_params = None
        for parameter_name, function_name in params.iteritems():
            for function_param, arguments in function_name.iteritems():
                function_arguments = {}
                if arguments is None:
                    function_arguments = {}
                elif type(arguments) != dict:
                    function_arguments['value'] = arguments
                else:
                    function_arguments = arguments
                function_arguments['count'] = self.question_count
                list_params = functions[function_param](function_arguments)
            self.question_params[parameter_name] = list_params


def test():
    print "Hello World"


def build_moodle_xml(yml_file=None, question=None, number_of_questions=10):
    from generators.generate_moodle_xml import gen_moodle_xml
    with open(yml_file, 'r') as stream:
        try:
            dict_value = yaml.load(stream)
            if question is not None:
                question = Question(dict_value[question], number_of_questions)
                print "--------Question Data--------"
                xml_builder = mxb.QuizBuilder(question.title)
                xml_builder.setup()
                for i in range(0, number_of_questions):
                    gen_moodle_xml(question)
                xml_builder.build_quiz_end_tag()
                print "-----------------------------"
            else:
                print dict_value
        except yaml.YAMLError as exc:
            print(exc)
