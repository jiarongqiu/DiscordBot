from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate

class Bot():

    def __init__(self,template,model='gpt-3.5-turbo-1106'):
        self.template = template

        self.llm = ChatOpenAI(
            model=model,
            streaming=True,
            temperature=0,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.template),
                ("human", "{question}"),
            ]
        )
        self.runner = self.prompt | self.llm |StrOutputParser()

    def __call__(self,question,context,stream=False):
        prompt = self.prompt.format(question=question,context=context)
        inputs = {"context":context,"question":question}
        if stream:
            res = self.runner.stream(inputs)
        else:
            res = self.runner.invoke(inputs)
        return res
    
    def custom_call(self,**kwargs):
        return self.runner.invoke(kwargs)


class SearchBot(Bot):
    TEMPLATE="""\
        You are an expert tasked with summarzing search result and answering questions about FileCoin.

        Generate a comprehensive and informative answer of 80 words or less for the \
        given question based solely on the provided search results in the context. You must \
        only use information from the provided search results. 

        Anything between the following `context`  html blocks is the search result retrieved from a knowledge \
        bank. 

        <context>
            {context} 
        <context/>
    """

    def __init__(self):
        super().__init__(self.TEMPLATE)

class SummerizeBot(Bot):
    TEMPLATE = """
        You are an expert tasked with summarzing description for documents.
        
        Generate a comprehensive and informative description of 50 words or less based on the context.

        Anything between the following `context` html blocks is the content of the documents. 
        <context>
            {context} 
        <context/>
        
        Remember to return the description only.
    """

    def __init__(self):
        super().__init__(template=self.TEMPLATE)

class SearchBotV2(Bot):
    TEMPLATE = """
        You are an expert tasked with summarizing search results and answering questions about FileCoin.
        Generate a comprehensive and informative answer of 80 words or less for the
        given question based solely on the provided search results in the context. You must
        only use information from the provided search results. Include the most relevant link from the search results 
        to support your answer.

        Below are the structured search results retrieved from a knowledge bank. Each entry consists of a description and associated links.

        {context}

        Your task is to provide a precise and concise response to the question, and also include the most relevant link from the search results that substantiates your answer.
    """

    def __init__(self):
        super().__init__(self.TEMPLATE)

search_bot = SearchBot()
search_bot_v2 = SearchBotV2()
summerize_bot = SummerizeBot()
