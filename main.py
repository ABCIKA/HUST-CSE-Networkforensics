import hashlib
import os.path
import urllib3
import json
from getExerciseList import get_exercise_list
from getAnswers import get_answers

loginUrl = 'https://222.20.126.100:50188/api/login'
coursesUrl = 'https://222.20.126.100:50188/api/course/info?level=1&pageIndex=1'
chaptersUrl = 'https://222.20.126.100:50188/api/course/chapter?courseId='
exercisesUrl = 'https://222.20.126.100:50188/api/course/learningInfo?chapterId='
submitAnswerUrl = 'https://222.20.126.100:50188/api/course/submit-answers'
Token = ''

courseId = ''
chapterId = ''
course_list = []
chapter_list = []
exercise_list = []


def login(url):

    username = input('请输入用户名：')
    password = input('请输入密码：')
    # 密码32位MD5加密
    password = hashlib.md5(password.encode()).hexdigest()
    fields = {
        'username': username,
        'password': password
    }
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    # 生成multipart/form-data的请求体
    form_data = urllib3.encode_multipart_formdata(fields)
    data = form_data[0]
    headers = {
        'Content-Type': form_data[1],
        'Content-Length': str(len(data)),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Authorization': 'Basic YmFpaG9uZ3NvZnQ6YmFpaG9uZ3NvZnQ='
    }
    # 发送POST请求,数据为form-data格式
    response = http.request('POST', url, headers=headers, body=data)
    if response.status == 200:
        res = json.loads(response.data.decode('utf-8'))
        token = res.get('access_token')
        print('登录成功！')
        # 短期内不需要重复登录，保存token
        with open('./token.json', 'w') as f:
            json.dump({'token': token}, f)
        return token
    else:
        print('登录失败！')
        return ''


def get_courses(url, token):
    headers = {
        'Authorization': 'Bearer ' + token
    }
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url, headers=headers)
    if response.status == 200:
        res = json.loads(response.data.decode('utf-8'))
        print(res)
        data = res.get('data')
        print(data)
        course_list = data.get('data')
        data_to_save = {"courses": course_list}
        # 保存课程列表
        with open('./courses/course_list.json', 'w') as f:
            json.dump(data_to_save, f, indent=4)
        return course_list


def get_chapters(url, token, course_id):
    headers = {
        'Authorization': 'Bearer ' + token
    }
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url + course_id, headers=headers)
    if response.status == 200:
        res = json.loads(response.data.decode('utf-8'))
        data = res.get('data')
        chapter_list = data.get('chapters')
        data_to_save = {"chapters": chapter_list}
        # 保存章节列表
        with open('./chapters/course'+course_id+'_chapter_list.json', 'w') as f:
            json.dump(data_to_save, f, indent=4)
        return chapter_list


# 登录
print('正在登录...')
if os.path.exists('./token.json'):
    with open('./token.json', 'r') as f:
        data = json.load(f)
        Token = data.get('token')
else:
    Token = login(loginUrl)
print('Token:', Token)
# 获取课程列表
print('正在获取课程列表...')
if os.path.exists('./courses/course_list.json'):
    with open('./courses/course_list.json', 'r') as f:
        data = json.load(f)
        course_list = data.get('courses', [])
else:
    course_list = get_courses(coursesUrl, Token)
# 输出课程列表
for course in course_list:
    print('课程ID：', course.get('auto_id'), '课程名称：', course.get('course_name'))
# 用户操作
option = -1
while option != 0:
    # 输入1获取课程列表，输入2以及课程ID获取章节列表，输入3以及章节ID获取习题列表，输入4以及章节ID获取答案，输入0退出
    print('1.获取课程列表 2.获取章节列表 3.获取习题列表 4.获取答案 0.退出')
    option = int(input('请输入操作编号：'))
    if option == 1:
        for course in course_list:
            print('课程ID：', course.get('auto_id'), '课程名称：', course.get('course_name'))
    elif option == 2:
        courseId = input('请输入课程ID：')
        if os.path.exists('./chapters/course'+courseId+'_chapter_list.json'):
            with open('./chapters/course'+courseId+'_chapter_list.json', 'r') as f:
                data = json.load(f)
                chapter_list = data.get('chapters', [])
        else:
            chapter_list = get_chapters(chaptersUrl, Token, courseId)
        for chapter in chapter_list:
            print('章节ID：', chapter.get('auto_id'), '章节名称：', chapter.get('chapter_name'))
    elif option == 3:
        chapterId = input('请输入章节ID：')
        if os.path.exists('./exercises/chapter' + chapterId + '_exercise_list.json'):
            with open('./exercises/chapter' + chapterId + '_exercise_list.json', 'r') as f:
                data = json.load(f)
                exercise_list = data.get('exercises', [])
        else:
            exercise_list = get_exercise_list(exercisesUrl + chapterId, Token, chapterId)
        for exercise in exercise_list:
            print('题目ID：', exercise.get('auto_id'))
            print('题目：', exercise.get('question_answer_info'))
            answer_type = exercise.get('answer_type')
            if answer_type == 1:
                print('题目类型：单选题')
            else:
                print('题目类型：多选题')
            student_options = exercise.get('childrens')
            for student_option in student_options:
                print('选项：', student_option.get('option'),'  ', student_option.get('question_answer_info'))
            print('------------------------------------')
    elif option == 4:
        chapterId = input('请输入章节ID：')
        if os.path.exists('./answers/chapter' + chapterId + '_answers.json'):
            with open('./answers/chapter' + chapterId + '_answers.json', 'r') as f:
                answers = json.load(f)
        else:
            answers = get_answers(submitAnswerUrl, Token, exercise_list, chapterId)
        for answer in answers:
            print('题目ID：', answer.get('question_id'))
            if os.path.exists('./exercises/chapter' + chapterId + '_exercise_list.json'):
                with open('./exercises/chapter' + chapterId + '_exercise_list.json', 'r') as f:
                    data = json.load(f)
                    exercise_list = data.get('exercises', [])
            else:
                exercise_list = get_exercise_list(exercisesUrl + chapterId, Token, chapterId)
            for exercise in exercise_list:
                if exercise.get('auto_id') == answer.get('question_id'):
                    print('题目：', exercise.get('question_answer_info'))
            print('答案：', answer.get('student_option'))



# 发送POST请求
# send_post_form_with_session_id(url, session_id, form_data)


# https://222.20.126.100:50188/api/course/learningInfo?chapterId=77 获取课程信息，包括课程习题
# 对于每道题，answer_type=1表示单选题，answer_type=2表示多选题
# https://222.20.126.100:50188/api/course/submit-answers 提交答案
# 请求数据格式如下：
# {answers: [{question_id: 1, student_option: "A"}],chapterId:"77"}
# 响应数据中isRight标识是否正确，为boolean类型
