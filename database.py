from Vkinter import candidates_collection, users_collection
import json

# for user in users_collection.find():
#     print(user)

top10_list =[]
for candidate in candidates_collection.find({'list_nidex': {'$lte': 10}}):
    selection = {
        'id': candidate['id'],
        'first_name': candidate['first_name'],
        'last_name': candidate['last_name'],
        'VK_page': candidate['VK_link'],
        'top_photos': candidate['top_photos']
    }
    top10_list.append(selection)
    # cursor = {}
    # print(candidate)
with open('candidates.json', 'w') as fi:
    json.dump(top10_list, fi, ensure_ascii=False, indent=4)

