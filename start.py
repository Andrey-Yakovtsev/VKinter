from Vkinter import User, Matching, get_params, candidates_collection, token, get_users_photos
import json



if __name__ == '__main__':

    get_user = str(input('Введите ID или Screenname пользователя для которого будем искать пару: '))
    target_user = User.search_user_by_name(token, get_user)
    print(target_user)
    search_list = 'фываолдж'
    # search_list = 'абвгдежзиклмнопрстуфхцчшщэюяАБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ' \
    #               'abcdefghijklmnopqrstuvwxyzABCDEFJHIGKLMNOPQRSTUVWXYZ'
    global_search_result = User.relation_ready_global_user_search(token, search_list)
    print('Всего нашли ==>', len(global_search_result))

    match = Matching()

    filtered_sex = match.matching_sex(target_user, global_search_result)
    print('Отобрали по полу ==>', len(filtered_sex))
    filtered_age = match.matching_age_delta(target_user, filtered_sex)
    print('Отранжировали по возрасту ==>')
    matched_location = match.matching_location(target_user, filtered_age)
    print('Отранжировали по локации ==>')
    friendship_relavity = match.friendship_relations(target_user, matched_location)
    print('Отранжировали по друзьям ==>')
    interest_matching = match.interests_intersection(target_user, friendship_relavity)
    print('Отранжировали по интересам ==>')

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

    top_rated_users = []
    i=1
    print('Получаем фотки лучших профилей ==>')
    for candidate in all_filters_result:
        if candidate['RATING'] >= top_points[-2]:
            candidate.update({'top_photos': get_users_photos(candidate['id'])})
            candidate.update({'VK_link': f"https://vk.com/{candidate['domain']}"})
            candidate.update({'list_index': i})
            top_rated_users.append(candidate)
            i+=1
    candidates_collection.delete_many({})
    candidates_collection.insert_many(top_rated_users)
    # candidate_list = candidates_collection.count_documents()
    # print(candidate_list)
    print()
    print()
    print()
    print("TOP10 КАНДИДАТОВ")
    print()
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
        print(selection)
    with open('candidates.json', 'w') as fi:
        json.dump(top10_list, fi, ensure_ascii=False, indent=4)

'''
задачи на 04 авг:
1. Выпилить ТОКЕН
2. подтянуть БД городов и стран для проверки ввода пользователем.
3. подтянуть прогрессбар...
4. написать тесты.

'''