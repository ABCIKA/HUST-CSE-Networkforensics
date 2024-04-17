import urllib3
import json


def get_exercise_list(url, token,chapterId):
    print('正在获取chapter'+chapterId+'习题列表...')
    headers = {
        'Authorization': 'Bearer ' + token  # 假设token类型是Bearer，根据实际情况调整
    }
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url, headers=headers)

    if response.status == 200:
        data = json.loads(response.data.decode('utf-8'))
        exercise_list = data.get('data', {}).get('exercises', [])

        if exercise_list:
            data_to_save = {"exercises": exercise_list}
            with open('./exercises/chapter'+chapterId+'_exercise_list.json', 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print("习题列表已保存到"+'./exercises/chapter'+chapterId+'_exercise_list.json')
        else:
            print("未找到习题列表数据。")
    else:
        print("请求失败！")
    return exercise_list
