import os.path
import json
from getExerciseList import get_exercise_list
from getAnswers import get_answers

# 替换为实际的URL和JESSIONID
exercisesUrl = 'https://222.20.126.100:50188/api/course/learningInfo?chapterId=77'
submitAnswerUrl = 'https://222.20.126.100:50188/api/course/submit-answers'
token = '422c6584-d9b1-43d4-b5d7-df63d1c5d06d'
chapterId = '77'
exercise_list = []

# 获取习题列表,若已有习题列表文件则直接读取，否则发送请求获取
if os.path.exists('./exercises/chapter' + chapterId + '_exercise_list.json'):
    with open('./exercises/chapter' + chapterId + '_exercise_list.json', 'r') as f:
        data = json.load(f)
        exercise_list = data.get('exercises', [])
else:
    exercise_list = get_exercise_list(exercisesUrl, token, chapterId)

# 获取答案
answers = get_answers(submitAnswerUrl, token, exercise_list, chapterId)
# 保存答案
with open('./answers/chapter' + chapterId + '_answers.json', 'w') as f:
    json.dump(answers, f, indent=4)
print(answers)


# 发送POST请求
# send_post_form_with_session_id(url, session_id, form_data)


# https://222.20.126.100:50188/api/course/learningInfo?chapterId=77 获取课程信息，包括课程习题
# 对于每道题，answer_type=1表示单选题，answer_type=2表示多选题
# https://222.20.126.100:50188/api/course/submit-answers 提交答案
# 请求数据格式如下：
# {answers: [{question_id: 1, student_option: "A"}],chapterId:"77"}
# 响应数据中isRight标识是否正确，为boolean类型
