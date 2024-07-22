import threading
import requests
import json
import logging
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
    
    def _add_docs_thread(self, url, max_depth):
        try:
            docs = crawler(url, max_depth=max_depth)
            sources = ["Crawled Sources:"]
            for doc in docs:
                sources.append(doc.metadata['source'])
            sources = "\n".join(sources)

            docs2 = crawler.chunk(docs)
            docs3 = crawler.from_docs(docs2)
            docs3 = crawler.llm_augment(docs3)
            vector_store.add_docs(docs3)
            crawler.visited.add(url)
            logging.info(f"Added {len(docs3)} documents to sources from {url}")
        except Exception as e:
            print("Error:", e)
            print(f"Error in processing {url}")

    def add_docs(self, url, max_depth=2):
        if url in crawler.visited:
            yield f"Url {url} has been added before"
            return
        thread = threading.Thread(target=self._add_docs_thread, args=(url, max_depth))
        thread.start()
        yield f"Added {url} to crawling queue. Please wait for a while."

api = API()