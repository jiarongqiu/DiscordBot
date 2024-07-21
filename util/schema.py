from enum import Enum

class Dir(Enum):
    URL = (1, 'url')
    API = (2, 'api')

    def __init__(self, id, path):
        self.id = id
        self.path = path

class MyDoc:

    def __init__(self, content, metadata):
        self._content = content
        self._metadata = {k:v for k,v in metadata.items() if v is not None and v.strip()!= ''}
    
    @staticmethod
    def from_docs(docs):
        res = []
        for doc in docs:
            res.append(MyDoc(doc.page_content, doc.metadata))
        return res
    
    @property
    def idx(self):
        return self.metadata.get('idx', -1)

    @property
    def page_content(self):
        return self._content
    
    @property
    def metadata(self):
        return self._metadata
    
    @page_content.setter
    def page_content(self, value):
        self._page_content = value

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def title(self):
        return self.metadata.get('title', '')
    
    @property
    def source(self):
        return self.metadata.get('source', '')
    
    @property
    def description(self):
        return self.metadata.get('description', '')
    
    @property
    def language(self):
        return self.metadata.get('language', '')
    
    @property
    def keywords(self):
        return self.metadata.get('keywords', [])
    
    @property
    def description_llm(self):
        return self.metadata.get('description_llm', '')
    
    @property
    def title_llm(self):
        return self.metadata.get('title_llm', '')
    
    @description_llm.setter
    def description_llm(self, value):
        self.metadata['description_llm'] = value
    
    @title_llm.setter
    def title_llm(self, value):
        self.metadata['title_llm'] = value
    
    @keywords.setter
    def keywords(self, value):
        self.metadata['keywords'] = value
    
    def __str__(self):
        return f"Source: {self.source}"