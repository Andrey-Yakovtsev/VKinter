'''
1. Какие классы кроме USER еще могут пригодиться?  DB_OBJECT?
2. БД - какую взять?


Последовательности:
1. Берем какого-то юзера (ID/Name)
2. Собираем его данные (пол, семейное положение (эти 2 параметра в отдельные таблички БД, для ускорения фильтрации)
 возраст(что делать с 18-), город, интересы(2-й этап))

3. Получаем список подходящих из 1000 (как обойти ограничение? и как сразу выкидывать малолетних и семейных?)
4. Фильтруем и сортируем по интересам
    (Веса: общий город - 50%,
    близкий возраст (или одинаковый) - 30%,
    наличие общих интересов - 20%
4.9 Проверяем наличие результатов в базе результатов (п.6) - выкидываем совпадения.
5. Выводим ТОР -10 в Джейсон. Можно имя файла обновлять, чтобы хранить результаты всех запросов.
6. Пишем вывод в БД результатов
'''

from pprint import pprint
import requests
import json
import datetime, time



OAUTH_URL = 'https://oauth.vk.com/authorize'
token = '75f6907e1aa79fed1222227787c392b151eed6eaec6c6edf20429648a6fd40eff4d001121b560aaa223fa'
OAUTH_PARAMS = {
    'client_id': '7493907', #ID  приложения которое просит доступ
    'display': 'page',
    'scope': 'notify, friends, photos, status, groups, offline',
    'response_type': 'token',
    'v': 5.89
}
# ID user от которого прошла строка 189983982

def get_params():
    return {
        'access_token': token,
        'v': 5.89,
    }

class User:
    def __init__(self, token):
        self.token = token


    def search_user_by_name(self, name):
        '''

        :param name: принимает имя строкой
        :return: список всех соответствующих именю юзеров, в статусе "готов к отношениям"
                И у кого указан год рождения
                Я пока выбираю из него первого в списке search_result[0]
        '''
        search_result = []
        params = get_params()
        params['q'] = name
        params['count'] = 50  # 999
        params['has_photo'] = 1  # без фотки не выводятся
        params['fields'] = 'sex, bdate, city, country, relation, verified, first_name, last_name,  nickname, occupation,' \
                           'interests, books, activities' \
                           'has_photo, common_count, is_friend'
        URL = 'https://api.vk.com/method/users.search'
        response = requests.get(URL, params)
        proper_status = '0156'  # Это статусы тех, кто открыто их объявил. Без указания статуса (None) исключены
        # print(response.text)

        for user in response.json()['response']['items']:
            current_year = datetime.datetime.now()
            if user.get('country'):
                if user.get('city'):
                    if str(user.get('relation')) in proper_status:
                        if user.get('bdate'):
                            if len(user.get('bdate').split('.')) == 3:
                                user_bdate = user['bdate'].split('.')
                                user_age = current_year.year - int(user_bdate[2])
                                if user_age >= 18:
                                    search_result.append(user)  # ['id'])
        print(f'Подходящий статус у {len(search_result)} результатов поиска. Берем 1-го из них')
        return search_result[0]  # можно впринципе пройтись разок поиском и все итоги убрать в базу


    def relation_ready_global_user_search(self, search_query: str):
        '''

        :param search_query: принимает строку символов (весь русский и латинский алфавит и цифры)
                            идет по каждому символу в цикле.
                            NB!!! Не забыть поменять параметр ['count'] на 999

        :return: выводит список "готовых к отношениям" и с указанным годом рождения
        '''
        mega_search_result = []
        i=1
        for symbol in search_query:
            params = get_params()
            params['q'] = symbol
            params['count'] = 999 #999
            params['has_photo'] = 1 # без фотки не выводятся
            params['fields'] = 'sex, bdate, city, country, relation, verified, first_name, last_name,  nickname, occupation,' \
                           'interests, books, activities' \
                           'has_photo, common_count, is_friend'

            URL = 'https://api.vk.com/method/users.search'
            response = requests.get(URL, params)
            time.sleep(0.4)
            print('Запрос:==>', i)
            i+=1
            proper_status = '0156' # Это статусы тех, кто открыто их объявил. Без указания статуса (None) исключены
            # print(response.text) # тут упоминается 241 млн записей: {"response":{"count":241720908,"items":...
            for user in response.json()['response']['items']:
                if str(user.get('relation')) in proper_status:
                    if user.get('bdate'):
                        if len(user.get('bdate').split('.')) == 3:
                            mega_search_result.append(user) #['id'])
        # print('Подходящий статус у ids==>', len(mega_search_result), mega_search_result) #, results_list)
        return mega_search_result #можно впринципе пройтись разок поиском и все итоги убрать в базу

'''
31/07 - итоги. Поиск собирает что надо.
Проблема только с выводом рейтингов по локейшнам. Надо проверить и поправить.
Осталось отобраьт ТОП-10 из получаемого списка и собрать для них ТОП-3 фото
"""(У тех людей, которые подошли по требованиям пользователю, получать топ-3 популярных фотографии с аватара. 
Популярность определяется по количеству лайков и комментариев.)""""

Возня с БАЗОЙ. Что икак туда заливать и зачем?
Продумать таблички
Попробовать загрузку...
'''



class Matching:
    '''
    функции проверки параметров соответствия юзеров из полученной базы нашему юзеру
    Получают на вход юзера, выдают рейтинги соответствия каждого юзера выбранному
    '''
    # matched_user = User.get_chosen_user_info(token)
    # user_sex = matched_user['sex']
    # user_bdate = matched_user['bdate'].split('.')
    # city = matched_user['city']['title']

    def matching_sex(self, user, search_result):
        '''

        :param user: Указывает на пользователя которому ищем пару
        :param search_result: Указывает вывод результатов поиска по которому идет сравнение
        :return: список с юзерами пола противоположеному от искомого юзера
        '''
        user_sex = user['sex']
        sex_appropriate_candidates = []
        for candidate in search_result:
            if candidate['sex'] != user_sex: #выборка оп полу
                sex_appropriate_candidates.append(candidate)
        print(len(sex_appropriate_candidates))
        return sex_appropriate_candidates

    def matching_age_delta(self, user, search_result):
        user_bdate = user['bdate'].split('.')
        current_year = datetime.datetime.now()
        user_age = current_year.year - int(user_bdate[2])
        for candidate in search_result:
            # print(len(search_result))
            if candidate.get('bdate'):
                # print(candidate.get('bdate'))
                candidate_age = current_year.year - int(candidate['bdate'].split('.')[2])
                # print(candidate_age)
                delta = abs(user_age - candidate_age)
                if delta <=3:
                    candidate.update({'matching_age': 100})
                    # print('100%', candidate['first_name'], candidate)
                if 4 <= delta <= 7:
                    candidate.update({'matching_age': 70})
                    # print('70%', candidate['first_name'], candidate)
                if 8 <= delta <= 15:
                    candidate.update({'matching_age': 30})
                    # print('30%', candidate['first_name'], candidate)
                if 16 <=delta <=100:
                    candidate.update({'matching_age': 10})
                    # print('10%', candidate['first_name'], candidate)
            else:
                print('Что-то из элса')
                candidate.update({'matching_age': 0})
        return search_result

    def matching_location(self, user, search_result):
        user_country = user['country']['id']
        user_city = user['city']['id']
        for candidate in search_result:
            if candidate.get('country'):
                if candidate['country']['id'] != user_country:
                    candidate.update({'matching_location': 30})
                else:
                    if candidate.get('city'):
                        if candidate['city']['id'] == user_city:
                            candidate.update({'matching_location': 100})
                        else:
                            candidate.update({'matching_location': 50})
                    else:
                        candidate.update({'matching_location': 30})
            else:
                candidate.update({'matching_location': 30})
        return search_result

    def friendship_relations(self, user, search_result):
        for candidate in search_result:
            if candidate['is_friend'] == 0:
                candidate.update({'friendship': 0})
            if candidate['is_friend'] == 1:
                candidate.update({'friendship': 100})
            if candidate['common_count'] == 1:
                candidate.update({'friendship_common': 50})
            if candidate['common_count'] == 0:
                candidate.update({'friendship_common': 0})
            else:
                candidate.update({'friendship_common': 0})
        return search_result

    def interests_intersection(self, user, search_result):
        user_interest_lookup_list = []
        if user.get('interests'):
            user_interests = user['interests'].split(', ')
            for item in user_interests:
                user_interest_lookup_list.append(item[:4])
        for candidate in search_result:
            if candidate.get('interests'):
                # print(candidate.get('interests'))
                candidate_interest_lookup_list = []
                candidate_interests = candidate['interests'].split(', ')
                for item in candidate_interests:
                    candidate_interest_lookup_list.append(item[:4])
                result = list(set(candidate_interest_lookup_list) & set(user_interest_lookup_list))
                if len(result) != 0:
                    candidate.update({'interest_common': 100})
                else:
                    candidate.update({'interest_common': 0})
            else:
                candidate.update({'interest_common': 0})

        return search_result




target_user = User.search_user_by_name(token,'Наталья Маликова')
print(target_user)
# search_list = 'фываолдж'
search_list = 'абвгдежзиклмнопрстуф'
global_search_result = User.relation_ready_global_user_search(token, search_list)
print('Всего нашли ==>', len(global_search_result))
# print(global_search_result)
match = Matching()
filtered_sex = match.matching_sex(target_user, global_search_result)
print('Отобрали по полу ==>', len(filtered_sex))

filtered_age = match.matching_age_delta(target_user, filtered_sex)
matched_location = match.matching_location(target_user, filtered_age)
friendship_relavity = match.friendship_relations(target_user, matched_location)
interest_matching = match.interests_intersection(target_user, friendship_relavity)

all_filters_result = interest_matching



all_ratings_list = []
for candidate in all_filters_result:
    rating = candidate['friendship_common'] + candidate['friendship'] + \
             candidate['matching_location'] + candidate['matching_age'] + \
             candidate['interest_common']
    candidate.update({'RATING': rating})
    all_ratings_list.append(rating)

top_points = sorted(set(all_ratings_list))
print('POINTS ==>', top_points)
def get_users_photos(candidate):
    params = get_params()
    params['owner_id'] = candidate
    params['album_id'] = 'profile'
    params['extended'] = 1
    params['photo_sizes'] = 1
    URL = 'https://api.vk.com/method/photos.get'
    response = requests.get(URL, params)
    time.sleep(0.4)
    # print(response.json())
    user_top_profile_photos = {}
    i=1
    for item in response.json()['response']['items']:
        # print('Likes amount ==>', item['likes']['count'], 'Link==>:', item['sizes'][-2]['url'])
        user_top_profile_photos.update(
            {f'photo{i}': {'likes_count': item['likes']['count']},
                            'url': item['sizes'][-2]['url']
             }
        )
        i+=1
    return user_top_profile_photos


for candidate in all_filters_result:
    top_10_candidates = []
    if candidate['RATING'] >= top_points[-4]:
        # try:
        candidate.update({'top_photos': get_users_photos(candidate['id'])})
        top_10_candidates.append(candidate)
        print(
            candidate['id'], candidate['first_name'], candidate['last_name'], candidate['bdate'], #candidate['country']['title'],
            candidate['RATING'],
            candidate['friendship_common'], candidate['friendship'],
            candidate['matching_location'], candidate['matching_age'],
            candidate['interest_common'], candidate['top_photos'])
        # except KeyError as e:
        #     print(e)
pprint(top_10_candidates)


''' все полученные на данном этапе результаты упаковываем в базу'''

# filter_top_10_results()