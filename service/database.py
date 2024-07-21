import os
import json
import tempfile
from pathlib import Path
from huggingface_hub import CommitScheduler
from datasets import load_dataset
from util.time import TimeUtil
from util.schema import Dir


class Database:

    LOCAL = os.path.join(tempfile.gettempdir(),"data")
    USERNAME = "JR818"
    REPO = "Web3"

    def __init__(self):
        try:
            self.scheduler = CommitScheduler(
                repo_id=self.REPO,
                repo_type="dataset",
                folder_path=self.LOCAL,
                token=os.getenv("HF_TOKEN")
            )
        except Exception as e:
            print(e)

    def load(self,dir:Dir):
        dataset = load_dataset(self.USERNAME+'/'+self.REPO,data_dir=dir.path,ignore_verifications=True,split="train")
        dataset = dataset.with_format("pandas").data.to_pandas()
        return dataset
    
    def write(self,data,dir:Dir):
        path = Path(self.LOCAL,dir.path) 
        path.mkdir(parents=True, exist_ok=True)
        path = path/f'{TimeUtil.get_date()}.json'
        try:
            data['datetime'] = TimeUtil.get_time()
            data = json.dumps(data)+"\n"
            with self.scheduler.lock:
                with path.open("a") as f:
                    f.write(data)
        except Exception as e:
            print(e)

database  = Database()
