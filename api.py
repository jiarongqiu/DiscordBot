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
            print(f"Processing {url}")
            logging.info(f"Processing {url}")
            docs = crawler(url, max_depth=max_depth)
            sources = ["Crawled Sources:"]
            for doc in docs:
                sources.append(doc.metadata['source'])
            sources = "\n".join(sources)    
            print(f"Sources:\n{sources}")
            docs2 = crawler.chunk(docs)
            docs3 = crawler.from_docs(docs2)
            print(f"Augmenting {len(docs3)} documents")
            logging.info(f"Augmenting {len(docs3)} documents")
            docs3 = crawler.llm_augment(docs3)
            print("Finished augmenting documents")
            vector_store.add_docs(docs3)
            print("Added documents to vector store")
            logging.info("Added documents to vector store")
            crawler.visited.add(url)
            print(f"Added {len(docs3)} documents to sources from {url}")
            logging.info(f"Added {len(docs3)} documents to sources from {url}")
        except Exception as e:
            print("Error:", e)
            print(f"Error in processing {url}")

    def add_docs(self, url, max_depth=2):
        if url in crawler.visited:
            return
        thread = threading.Thread(target=self._add_docs_thread, args=(url, max_depth))
        thread.start()

api = API()