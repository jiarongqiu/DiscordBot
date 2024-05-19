import requests

class API:
    ENDPOINT = 'https://jr818-jarvisfastapi.hf.space/api'

    def get_suggestion(self, inputs):
        url = f'{self.ENDPOINT}/suggestion?inputs={inputs}'
        response = requests.get(url)
        return response.json()
    
    def get_answer(self, inputs):
        url = f'{self.ENDPOINT}/answer?inputs={inputs}'
        response = requests.get(url,stream=True)
        try:
            for line in response:
                yield line
        finally:
            response.close()

api = API()