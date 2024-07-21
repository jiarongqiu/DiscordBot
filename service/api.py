import os
import time
import json
import requests
from typing import Any
from .llm import search_bot,search_bot_v2
from .vector_store import vector_store
# from .logger import logger
from util.time import TimeUtil
from .database import database
from util.schema import Dir


class API():


    def __init__(self) -> None:
        pass

    def search(self,query,**kwargs):
        if not query:
            return []
        docs = vector_store.search(query,**kwargs)
        return docs
    
    def marginal_search(self,query,**kwargs):
        if not query:
            return []
        docs = vector_store.marginal_search(query,**kwargs)
        return docs

    def get_suggestion(self,query):
        if not query:
            return []
        docs = vector_store.marginal_search(query,lambda_mult=0.6)
        res = []
        for doc in docs:
            name = doc.metadata.get('title_llm','')
            url = doc.metadata.get('source','')
            if name == '' or url == '':
                continue
            res.append({"name":name,"url":url})
        database.write({"query":query,"api":'auto_complete',"result":res},dir=Dir.API)
        return res
    
    def get_answer(self,query):
        docs = vector_store.search(query)
        source = []
        context = []
        for doc in docs:
            if doc.metadata['score']<0.2:
                continue
            if 'title_llm' in doc.metadata:
                source.append({
                    "name":doc.metadata.get('title_llm',''),
                    "url":doc.metadata.get('source',''),
                    "description":doc.metadata.get('description_llm','')
                })
            context.append(doc.metadata.get('description',''))
        # yield json.dumps(source)
        context = "\n".join(context)
        answer = search_bot(query,context,stream=True)
        text = ""
        for i in answer:
            text += i
            yield i
        database.write({"query":query,"api":'search',"result":text},dir=Dir.API)
    
    def get_answer_v2(self,query):
        docs = vector_store.search(query)
        source = []
        context = []
        for doc in docs:
            if doc.metadata['score']<0.2:
                continue
            if 'title_llm' in doc.metadata:
                source.append({
                    "name":doc.metadata.get('title_llm',''),
                    "url":doc.metadata.get('source',''),
                    "description":doc.metadata.get('description_llm','')
                })
            description = doc.metadata.get('description','')
            links = doc.metadata.get('source','')
            context.append(f"<context>Description: {description}\nLinks: {links}\n<context/>")
        # yield json.dumps(source)
        # print(context)
        context = "\n".join(context)
        answer = search_bot_v2(query,context,stream=True)
        text = ""
        for i in answer:
            text += i
            yield i
        database.write({"query":query,"api":'answer_v2',"result":text},dir=Dir.API)

    def get_filecoin_price(self):
        url="https://api.spacescope.io/v2/price/realtime"
        headers = {
        'authorization': f'Bearer {os.environ["SPACESCOPE_API_KEY"]}'
        }
        data = None
        try:
            response = requests.get(url, headers=headers)
            data = round(json.loads(response.text)['data']['price'],3)
        except Exception as e:
            print(e)
        return data
    
    def get_filecoin_deposit(self):
        url = "https://api.spacescope.io/v2/fvm/defi/leaderboard_summary_combined"
        # url="https://api.spacescope.io/v2/fvm/defi/all_protocol_flow?start_date={}&end_date={}".format(TimeUtil.get_date(offset=-2,format='%Y-%m-%d'),TimeUtil.get_date(offset=-1,format='%Y-%m-%d'))
        headers = {'authorization': f'Bearer {os.environ["SPACESCOPE_API_KEY"]}'}
        data = None
        try:
            response = requests.get(url, headers=headers)
            data = json.loads(response.text)
            data = data['data'][-1]['inflow_fil']
            data = f"{data:,.0f}"
        except Exception as e:
            print(e)
        return data
    
    def get_filecoin_tvl(self):
        data = None
        try:
            url="https://api.llama.fi/v2/chains"
            res=requests.get(url=url)
            data = json.loads(res.text)
            data = [e for e in data if e['name'] =='Filecoin'][0]['tvl']
            data = f"{data:,.1f}"
        except Exception as e:
            print(e)
        return data
    
    def get_fvm_storage(self):
        url = "https://dashboard.starboard.ventures/v2/v1/network_core/capacity-services/network_storage_capacity"
        response = requests.get(url)
        data=response.json()['data'][0]
        total_raw_bytes_power = int(data['total_raw_bytes_power'])/1024**6
        total_raw_bytes_power = f"{total_raw_bytes_power:,.1f}"
        return total_raw_bytes_power
    
    def get_fvm_active_deal(self):
        url="https://dashboard.starboard.ventures/v2/v1/network_core/market-deals/deal_states_aggregate_daily"
        response = requests.get(url)
        data = response.json()['data'][0]
        active_deals_verified_bytes = int(data['active_deals_verified_bytes'])/1024**6
        active_deals_verified_bytes = f"{active_deals_verified_bytes:,.1f}"
        return active_deals_verified_bytes

api = API()