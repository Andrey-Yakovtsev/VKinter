from pymongo import MongoClient
import requests
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

'''заводим БД'''
client = MongoClient()
vkinterdb = client['VKinter']
users_collection = vkinterdb['users']
candidates_collection = vkinterdb['candidates']

def get_params():
    return {
        'access_token': token,
        'v': 5.89,
    }

class User:
    def __init__(self, token):
        self.token = token

    def search_user_by_name(self, id):
        '''

        :param name: принимает имя строкой
        :return: список всех соответствующих именю юзеров, в статусе "готов к отношениям"
                И у кого указан год рождения
                Я пока выбираю из него первого в списке search_result[0]
        '''
        params = get_params()
        params['user_ids'] = id
        params['fields'] = 'sex, bdate, city, country, relation, first_name, last_name,' \
                           'interests,common_count, is_friend'
        URL = 'https://api.vk.com/method/users.get'
        response = requests.get(URL, params)
        print(response.text)
        for user in response.json()['response']:
            current_year = datetime.datetime.now()
            if user.get('country') is None:
                country_name = str(input('Не указана страна! Укажите где живет пользователь!: '))
                user.update({'country': {'id': '', 'title': country_name}})
            if user.get('city') is None:
                city_name = str(input('Не указан город! Укажите город, где живет пользователь!: '))
                user.update({'city': {'id': '', 'title': city_name}})
            if user.get('bdate') is None:
                user_bdate = int(input("У пользователя не указан год рождения. Укажите год (в формате 0000): "))
                user_age = current_year.year - user_bdate
                user.update({'bdate': f'1.1.{user_bdate}'})
                if user_age < 18:
                    print("Этот человек еще несовершеннолетний. Конец поиска.")
                    break
            else:
                if len(user.get('bdate').split('.')) == 3:
                    user_bdate = user['bdate'].split('.')
                    user_age = current_year.year - int(user_bdate[2])
                    if user_age < 18:
                        print("Этот человек еще несовершеннолетний. Конец поиска.")
                        break

                if len(user.get('bdate').split('.')) != 3:
                    user_bdate = int(input("У пользователя не указан год рождения. Укажите год (в формате 0000): "))
                    user_age = current_year.year - user_bdate
                    user.update({'bdate': f'1.1.{user_bdate}'})
                    if user_age < 18:
                        print("Этот человек еще несовершеннолетний. Конец поиска.")
                        break

        users_collection.delete_many({})
        users_collection.insert_one(user)
        return user


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
            params['fields'] = 'sex, bdate, city, country, relation, domain, first_name, last_name,' \
                           'interests, books, common_count, is_friend'
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


class Matching:
    '''
    функции проверки параметров соответствия юзеров из полученной базы нашему юзеру
    Получают на вход юзера, выдают рейтинги соответствия каждого юзера выбранному
    '''

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
        return sex_appropriate_candidates

    def matching_age_delta(self, user, search_result):
        user_bdate = user['bdate'].split('.')
        current_year = datetime.datetime.now()
        user_age = current_year.year - int(user_bdate[2])
        for candidate in search_result:
            if candidate.get('bdate'):
                candidate_age = current_year.year - int(candidate['bdate'].split('.')[2])
                delta = abs(user_age - candidate_age)
                if delta <=3:
                    candidate.update({'matching_age': 100})
                if 4 <= delta <= 7:
                    candidate.update({'matching_age': 70})
                if 8 <= delta <= 15:
                    candidate.update({'matching_age': 30})
                if 16 <=delta <=100:
                    candidate.update({'matching_age': 10})
            else:
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


def get_users_photos(candidate):
    params = get_params()
    params['owner_id'] = candidate
    params['album_id'] = 'profile'
    params['extended'] = 1
    params['photo_sizes'] = 1
    URL = 'https://api.vk.com/method/photos.get'
    response = requests.get(URL, params)
    time.sleep(0.4)
    if response.json()['response']['count'] >3:
        likes_counter = []
        for item in response.json()['response']['items']:
            likes_counter.append(item['likes']['count'])
        top3_likes = list(reversed(sorted(likes_counter)))
        many_photos_crop_list = []
        for item in response.json()['response']['items']:
            if item['likes']['count'] in top3_likes[0:3]:
                photo = {'Likes': item['likes']['count'], 'Link': item['sizes'][-2]['url']}
                many_photos_crop_list.append(photo)
        return many_photos_crop_list
    else:
        user_top_profile_photos = []
        for item in response.json()['response']['items']:
            photo = {'Likes': item['likes']['count'], 'Link': item['sizes'][-2]['url']}
            user_top_profile_photos.append(photo)
        return user_top_profile_photos
