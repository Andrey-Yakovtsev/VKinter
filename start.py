from Vkinter import User, Matching, token, show_me_top_10, show_me_hi_rated, do_me_a_json

if __name__ == '__main__':

    trg_user = User(token)
    match = Matching()

    target_user = trg_user.search_user(
        str(
            input(
                'Введите ID или Screenname пользователя для которого будем искать пару: '
            )
        )
    )

    global_search_result = trg_user.relation_ready_global_user_search()

    filtered_age = match.matching_age_delta(target_user, global_search_result)

    matched_location = match.matching_location(target_user, filtered_age)

    friendship_relavity = match.friendship_relations(target_user, matched_location)

    interest_matching = match.interests_intersection(target_user, friendship_relavity)

    all_filters_result = interest_matching

    show_me_hi_rated(all_filters_result)
    print("TOP-10 Кандидатов:")
    for candidate in show_me_top_10():
        print(candidate)
    do_me_a_json()


'''
Украшалки:
1. подтянуть БД городов и стран для проверки ввода пользователем.
2. подтянуть прогрессбар...
'''