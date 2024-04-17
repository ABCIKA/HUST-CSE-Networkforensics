import urllib3
import json
import time


def generate_combinations(options, current_combination=[], index=0):
    if index == len(options):
        if len(current_combination) > 1:  # 只保存包含至少两个选项的组合
            return [",".join(current_combination)]
        else:
            return []

    combinations = []
    combinations.extend(generate_combinations(options, current_combination + [options[index]], index + 1))
    combinations.extend(generate_combinations(options, current_combination, index + 1))
    return combinations


def get_exercises_and_options(exercise_list):
    exercises = []
    for exercise in exercise_list:
        answer_type = exercise.get('answer_type')
        options = []
        question_id = exercise.get('auto_id')
        option_list = []
        for child in exercise.get('childrens', []):
            options.append(child.get('option'))
        # 如果为多选题，穷举所有选项组合
        if answer_type == 2:
            option_list = generate_combinations(options)

        exercises.append({
            'question_id': question_id,
            'answer_type': answer_type,
            'options': options,
            'option_list': option_list
        })
    return exercises


def get_answers(url, token, exercise_list, chapterId):
    headers = {
        'Authorization': 'Bearer ' + token  # 假设token类型是Bearer，根据实际情况调整
    }
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    # 获取习题和选项
    exercises = get_exercises_and_options(exercise_list)
    right_answers = []
    not_right_answers = []
    not_right_answers_num = 0
    submint_num = 1
    # 初始化答案
    for exercise in exercises:
        right_answers.append({
            'question_id': exercise.get('question_id'),
            'student_option': '',
            'isRight': False
        })
        not_right_answers_num += 1
        answer_type = exercise.get('answer_type')
        options = exercise.get('options')
        option_list = exercise.get('option_list')
        if answer_type == 1:
            not_right_answers.append({
                'question_id': exercise.get('question_id'),
                'student_option': options[0],
                'option_number': 0
            })
        else:
            not_right_answers.append({
                'question_id': exercise.get('question_id'),
                'student_option': option_list[0],
                'option_number': 0
            })
    # 初次提交答案
    form_data = {
        'answers': [],
        'chapterId': chapterId
    }
    for i in range(len(exercises)):
        form_data['answers'].append({
            'question_id': exercises[i].get('question_id'),
            'student_option': not_right_answers[i].get('student_option')
        })
    print('form_data:', form_data)
    response = http.request('POST', url, headers=headers, body=json.dumps(form_data))
    print('第'+str(submint_num)+'次提交')
    submint_num += 1
    if response.status == 200:
        res = json.loads(response.data.decode('utf-8'))
        data = res.get('data')
        for answer in data.get('answers', []):
            question_id = answer.get('question_id')
            is_right = answer.get('isRight')
            if is_right is True:
                for i in range(len(right_answers)):
                    if right_answers[i].get('question_id') == question_id:
                        if right_answers[i].get('isRight') is False:
                            right_answers[i]['student_option'] = not_right_answers[i].get('student_option')
                            right_answers[i]['isRight'] = True
                            not_right_answers_num -= 1
                            print('right_answers_id', right_answers[i].get('question_id'))
                            print('not_right_answers_num', not_right_answers_num)
    # 延迟5秒
    time.sleep(5)
    # 穷举答案
    while not_right_answers_num > 0:
        form_data = {
            'answers': [],
            'chapterId': chapterId
        }
        for i in range(len(exercises)):
            if right_answers[i].get('isRight') is False:
                if exercises[i].get('answer_type') == 1:
                    not_right_answers[i]['option_number'] += 1
                    option_number = not_right_answers[i].get('option_number')
                    not_right_answers[i]['student_option'] = exercises[i].get('options')[option_number]
                else:
                    not_right_answers[i]['option_number'] += 1
                    option_number = not_right_answers[i].get('option_number')
                    not_right_answers[i]['student_option'] = exercises[i].get('option_list')[option_number]

                form_data['answers'].append({
                    'question_id': exercises[i].get('question_id'),
                    'student_option': not_right_answers[i].get('student_option')
                })
            else:
                form_data['answers'].append({
                    'question_id': exercises[i].get('question_id'),
                    'student_option': right_answers[i].get('student_option')
                })
        response = http.request('POST', url, headers=headers, body=json.dumps(form_data))
        print('第'+str(submint_num)+'次提交')
        submint_num += 1
        if response.status == 200:
            res = json.loads(response.data.decode('utf-8'))
            data = res.get('data')
            for answer in data.get('answers', []):
                question_id = answer.get('question_id')
                is_right = answer.get('isRight')
                if is_right is True:
                    for i in range(len(right_answers)):
                        if right_answers[i].get('question_id') == question_id:
                            if right_answers[i].get('isRight') is False:
                                right_answers[i]['student_option'] = not_right_answers[i].get('student_option')
                                right_answers[i]['isRight'] = True
                                not_right_answers_num -= 1
                                print('right_answers_id', right_answers[i].get('question_id'))
                                print('not_right_answers_num', not_right_answers_num)
        # 延迟5秒
        time.sleep(5)

    return right_answers
