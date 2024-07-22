import json
import re
from tqdm import tqdm
from bs4 import BeautifulSoup
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from service.llm import Bot
from util.schema import MyDoc
from typing import List

class Crawler(RecursiveUrlLoader):

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
    }
    CHUNK_SIZE = 2000
    TEMPLATE = """
        You are an expert in refining and summarization based on the title, description of the document to make it more concise and informative. Please generate a refined title, description, and keywords for the document in json format. 
        Remember, the generated keywords should be less than 3 words, the generated title should be less than 10 words, and the generated description should be less than 100 words.
        Here is a legal example of the json format:
        {{
            "title": "The Title of the Document",
            "description": "The Description of the Document",
            "keywords": ["keyword1", "keyword2", "keyword3"]
        }}
    """

    def __init__(self,keywords=[]):
        self.keywords = keywords
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=self.CHUNK_SIZE, chunk_overlap=200)
        self.bot = Bot(template=self.TEMPLATE)
        self.visited = set()
        super().__init__(
            url="",
            extractor=self._extractor,
            timeout=600,
            headers=self.HEADERS,
            exclude_dirs=[],
            prevent_outside=True
        )

    def _extractor(self,html: str) -> str:
        text = BeautifulSoup(html, "lxml").get_text(" ")
        text = re.sub(r"\n\n+", "\n\n", text)
        text = re.sub(r"\s\s+", "  ", text).strip()
        if self.check_keywords(text):
            return text
        return
    
    def check_keywords(self,text):
        if not self.keywords:
            return True
        for key in self.keywords:
            if key in text:
                return True
        return False

    def __call__(self,url,max_depth=2,prevent_outside=True):
        self.url = url
        self.base_url = url
        self.max_depth = max_depth
        self.prevent_outside = prevent_outside
        docs = list(self._get_child_links_recursive(url, self.visited))
        return docs
    
    def from_docs(self,docs):
        return MyDoc.from_docs(docs)
    
    def chunk(self,docs):
        res = []
        for doc in docs:
            res += self.splitter.split_documents([doc])
        return res
    
    def llm_augment(self,docs:List[MyDoc]):
        question_template = """
        Please generate a refined title, description, and keywords for the document
        1. title:{title}
        2. desription:{description}
        3. content:{content}
        """     
        res =[]
        for doc in docs:
            print(doc.title)
            question = question_template.format(
                title=doc.title,
                description=doc.description,
                content=doc.page_content
            )
            response = self.bot.custom_call(question=question)
            try:
                response = response.strip('`').strip('json\n')
                data = json.loads(response)
                doc.keywords = data['keywords']
                doc.description_llm = data['description']
                doc.title_llm = data['title']
                res.append(doc)
            except Exception as e:
                print("x")
                print(e,response)
        return res   
    
crawler = Crawler()