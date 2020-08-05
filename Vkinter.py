from pymongo import MongoClient
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

    def search_user(self, id):


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
                user.update({'age': user_age})
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

    def extract_user_age(self):
        for user in users_collection.find():
            u_age = user['age']
        return u_age

    def extract_user_contr_sex(self):
        for user in users_collection.find():
            u_sex = user['sex']
            if u_sex == 1:
                return 2
            if u_sex == 2:
                return 1

    def relation_ready_global_user_search(self):
        '''
        :param search_query: принимает строку символов (весь русский и латинский алфавит и цифры)
                            идет по каждому символу в цикле.
        :return: выводит список "готовых к отношениям" и с указанным годом рождения в диапазоне ОТ ДО
        '''
        user_age = self.extract_user_age()
        mega_search_result = []
        i=1
        search_list = 'фываолдж'
        # search_list = "абвгдежзиклмнопрстуфхцчшщэюя"
        # search_list = 'абвгдежзиклмнопрстуфхцчшщэюяАБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ' \
        #               'abcdefghijklmnopqrstuvwxyzABCDEFJHIGKLMNOPQRSTUVWXYZ'

        for symbol in search_list:
            params = get_params()
            params['q'] = symbol
            params['count'] = 999 #999
            params['sex'] = self.extract_user_contr_sex()
            params['age_from'] = 18
            params['age_to'] = 50
            params['has_photo'] = 1 # без фотки не выводятся
            params['fields'] = 'sex, bdate, city, country, relation, domain, first_name, last_name,' \
                           'interests, books, common_count, is_friend'
            URL = 'https://api.vk.com/method/users.search'
            response = requests.get(URL, params)
            time.sleep(0.4)
            print(f'Запрос:==> {i} из {len(search_list)}')
            i+=1
            proper_status = '0156' # Это статусы тех, кто открыто их объявил. Без указания статуса (None) исключены
            for user in response.json()['response']['items']:
                if str(user.get('relation')) in proper_status:
                    if user.get('bdate'):
                        if len(user.get('bdate').split('.')) == 3:
                            mega_search_result.append(user)
        print('Всего нашли ==>', len(mega_search_result))
        return mega_search_result


class Matching:
    '''
    функции проверки параметров соответствия юзеров из полученной базы нашему юзеру
    Получают на вход юзера, выдают рейтинги соответствия каждого юзера выбранному
    '''

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
        print('Отранжировали по возрасту ==>')
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
        print('Отранжировали по локации ==>')
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
        print('Отранжировали по друзьям ==>')
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
        print('Отранжировали по интересам ==>')
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

def show_me_hi_rated(all_filters_result):
    all_ratings_list = []
    for candidate in all_filters_result:
        rating = candidate['friendship_common'] + candidate['friendship'] + \
                 candidate['matching_location'] + candidate['interest_common'] + \
                 candidate['matching_age']
        candidate.update({'RATING': rating})
        all_ratings_list.append(rating)
    top_points = sorted(set(all_ratings_list))
    print(f'Всего в рейтинге баллов от {top_points[0]} до ==>{top_points[-1]}')
    top_rated_users = []
    i = 1
    print(f'Получаем фотки лучших профилей с рейтингом {top_points[-1]} и {top_points[-2]} ==>')
    for index, candidate in enumerate(all_filters_result):
        if candidate['RATING'] >= top_points[-2]:
            candidate.update({'top_photos': get_users_photos(candidate['id'])})
            candidate.update({'VK_link': f"https://vk.com/{candidate['domain']}"})
            candidate.update({'list_index': i})
            top_rated_users.append(candidate)
            i += 1
    candidates_collection.delete_many({})
    candidates_collection.insert_many(top_rated_users)

    return top_rated_users

def show_me_top_10():
    top10_list =[]
    for candidate in candidates_collection.find({'list_index': {'$lte': 10}}):
        selection = {
            'RATING': candidate['RATING'],
            'id': candidate['id'],
            'first_name': candidate['first_name'],
            'last_name': candidate['last_name'],
            'VK_page': candidate['VK_link'],
            'top_photos': candidate['top_photos']
        }
        top10_list.append(selection)

    return top10_list

def do_me_a_json():
    with open('candidates.json', 'w') as fi:
        json.dump(show_me_top_10(), fi, ensure_ascii=False, indent=4)

def get_countries_list():
    pass

def get_cities_list():
    pass