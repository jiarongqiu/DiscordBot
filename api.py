import requests
import json
from service.crawler import crawler
from service.vector_store import vector_store

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

    def add_docs(self, url, max_depth=2):
        try:
            yield f"Start crawling {url} with max depth {max_depth}"
            if url in crawler.visited:
                yield f"Url {url} has been added before"
            docs = crawler(url,max_depth=max_depth)
            sources = ["Crwawled Sources:"]
            for doc in docs:
                # print(doc.metadata['source'])
                sources.append(doc.metadata['source'])
            sources = "\n".join(sources)
            yield sources
            docs2 = crawler.chunk(docs)
            docs3 = crawler.from_docs(docs2)
            docs3 = crawler.llm_augment(docs3)
            vector_store.add_docs(docs3)
            yield f"Add {len(docs3)} documents to sources"
        except Exception as e:
            print("Error:", e)
            yield f"Error in processing {url}"

api = API()