from qgen import functions
from random import choice as random_choice,randint
from qgen_exceptions import EvaluationException

"""Helper functions that are essential to the construction of questions"""

# to help decide if a question is valid
question_list = []


def evaluate_blocks(text, params):
    """Evaluates the code blocks delimited by a $ in a question's answer or distractor"""
    text = text.replace("\$", "esCA")
    if text.count("$") % 2 != 0:
        raise EvaluationException("Incorrect number of $ found in a block")
    while "$" in text:
        start_index = text.index('$')
        end_index = text.index('$', start_index + 1) + 1

        # get code to be evaluated
        substr = text[start_index:end_index]

        # remove leading and trailing $
        eval_block = substr[1:-1]

        text = text.replace(substr, str(eval(eval_block)))
    text = text.replace("esCA", "$")
    return text


def evaluate_functions(text, params):
    """Evaluates the functions delimited by a @ in a question's answer or distractor"""
    while "@" in text:
        start_index = text.index('@')
        end_index = text.index('@', start_index + 1) + 1
        substr = text[start_index:end_index]

        eval_block = substr[1:-1]
        # find function
        function_name = eval_block

        text = text.replace(substr, str(functions[function_name](params)))
    return text


def evaluate_braces(text, params, params_cache):
    """Evaluates variables enclosed in braces which denotes a set"""
    while "[" in text:
        start_index = text.index('[')
        end_index = text.index(']', start_index + 1) + 1
        substr = text[start_index:end_index]

        eval_block = substr[1:len(substr) - 1]

        choices = eval_block.split(",")
        variables = []
        unwanted = []

        for choice in choices:
            choice = choice.strip()
            if choice == "all":
                for var in params_cache:
                    if params_cache[var]:
                        variables.append(var.strip())
            elif choice[0] == '~':
                var = choice[1:].strip()
                if var in params:
                    unwanted.append(var)
                else:
                    unwanted.append(choice)
            else:
                if params_cache[choice]:
                    variables.append(choice)
            for var in unwanted:
                if var in variables:
                    variables.remove(var)

        index = randint(0, len(variables) - 1)
        result = random_choice(params_cache[variables[index]])
        text = text.replace(substr, str(result))
    return text


def validate_question(body, answers, distractors):
    answers, distractors = validate_answer_distractor(answers, distractors)
    if answers:
        if not valid_question(body, answers, distractors):
            return None
        return body, answers, distractors
    else:
        return None


def valid_question(body, answers, distractors):
    description = (body,set(answers),set(distractors))
    is_valid = description in question_list
    question_list.append(description)
    return is_valid


def validate_answer_distractor(answers, distractors):
    answer_list = []
    distractor_list = []
    for answer in answers:
        if answer not in answer_list:
            answer_list.append(answer)
    for distractor in distractors:
        if distractor not in distractor_list:
            distractor_list.append(distractor)
    return answer_list, distractor_list
