import requests
import json

class API:
    ENDPOINT = 'https://jr818-jarvisfastapi.hf.space/api'

    def get_suggestion(self, inputs):
        url = f'{self.ENDPOINT}/suggestion?inputs={inputs}'
        response = requests.get(url)
        return response.json()
    
    def get_answer(self, inputs):
        data = {'inputs': inputs}
        url = f'{self.ENDPOINT}/answer_v2'
        response = requests.post(url,data=json.dumps(data),stream=True)
        try:
            for line in response:
                yield line
        finally:
            response.close()

api = API()