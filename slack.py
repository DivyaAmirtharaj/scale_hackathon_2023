import requests

class SlackAPIManager:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
        }
        self.base_url = "https://slack.com/api/"

    def make_api_call(self, endpoint, params=None, method='GET'):
        url = f'{self.base_url}{endpoint}'
        response = requests.request(method, url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Request failed with status {response.status_code}')

    def get_conversation_history(self, conversation_id):
        endpoint = 'conversations.history'
        params = {'channel': conversation_id}
        return self.make_api_call(endpoint, params=params)
    
    def get_conversation_list(self):
        endpoint = 'conversations.list'
        return self.make_api_call(endpoint)
    
    def get_user_list(self):
        endpoint = 'users.list'
        return self.make_api_call(endpoint)
