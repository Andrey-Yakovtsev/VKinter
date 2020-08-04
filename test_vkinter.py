import unittest
from Vkinter import get_params, candidates_collection, users_collection
import requests



class Test_Vkinter(unittest.TestCase):

    def test_user_search(self):
        params = get_params()
        params['user_ids'] = 'ayakovtsev'
        params['fields'] = 'sex, bdate, screen_name, city, country, relation, first_name, last_name,' \
                           'interests,common_count, is_friend'
        URL = 'https://api.vk.com/method/users.get'
        response = requests.get(URL, params)
        for user in response.json()['response']:
            self.assertEqual(user['screen_name'], 'ayakovtsev')

    def test_relation_ready_search(self):
        params = get_params()
        params['q'] = 'q'
        params['count'] = 1
        URL = 'https://api.vk.com/method/users.search'
        response = requests.get(URL, params)
        self.assertIsNotNone(response.json()['response'])

    def test_matching_sex(self):
        for user in users_collection.find():
            u_sex = user['sex']
        for candidate in candidates_collection.find():
            cand_sex = candidate['sex']
            self.assertNotEqual(u_sex, cand_sex)

if __name__ == '__main__':
    unittest.main()