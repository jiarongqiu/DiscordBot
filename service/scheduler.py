import datetime
import json
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from .api import api
from .vector_store import vector_store

class Scheduler:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = [self.update_filecoin_stat,self.update_filecoin_data_stat]
    
    def run(self):
        for job in self.jobs:
            self.scheduler.add_job(job, 'interval', minutes=5)
        self.scheduler.start()

    def update_filecoin_stat(self):
        price = api.get_filecoin_price()
        deposit = api.get_filecoin_deposit()
        # tvl = api.get_filecoin_tvl()
        # total_raw_bytes_power = api.get_fvm_storage()
        active_deals_verified_bytes = api.get_fvm_active_deal()
        text  = """
            The price of filecoin(FIL) is currently ${} USD.
            The Total DeFi Net Deposits of filecoin(FIL) is {} FIL.
            The Total Value Locked(TVL) of filecoin(FIL) is {} FIL.
            The Total Active Filecoin Deals of the Filecoin Network is {} EiB.
        """.format(price,deposit,deposit,active_deals_verified_bytes)
        # print(f"Update {text}")
        vector_store.upsert(text,"dataset_1",source='https://fvm.starboard.ventures/explorer/leaderboard?utm_source=Starboard-TLDR-HTS')
    
    def update_filecoin_data_stat(sefl):
        total_raw_bytes_power = api.get_fvm_storage()
        text  = """The storage capacity of the Filecoin Network is {} EiB. The Network Raw Byte Power of the Filecoin Network is {} EiB. 
        """.format(total_raw_bytes_power,total_raw_bytes_power)
        # print(f"Update {text}")
        vector_store.upsert(text,"dataset_2",source='https://dashboard.starboard.ventures/dashboard')
        

