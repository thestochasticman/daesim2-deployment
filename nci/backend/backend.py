from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict
from typing import List, Dict
import pandas as pd
import paramiko
import os
import uuid

USER = 'ya6227'
HOST = 'gadi.nci.org.au'
KEY_PATH = '/Users/yasar/.ssh/id_rsa'
DATA_DIR = '/g/data/xe2/ya6227/daesim2-analysis/DAESIM_data/DAESIM_jobs'
 
app = FastAPI()

class DataInput(BaseModel):
  params: Dict[str, float]
  filename: str
  dataframe: List[Dict]

def upload_to_gadi(df: pd.DataFrame, filename: str) -> str:
  job_id = str(uuid.uuid4())[:8]
  filename = f"input_{job_id}.csv"
  local_path = f"/tmp/{filename}"
  remote_path = os.path.join(DATA_DIR, filename)

  # Save locally
  df.to_csv(local_path, index=False)
  print(local_path)
  # SSH and uploa
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(HOST, username=USER, key_filename=KEY_PATH)
  assert os.path.exists(local_path), f"Local file missing: {local_path}"
  sftp = ssh.open_sftp()
  sftp.put(local_path, remote_path)
  sftp.close()
  ssh.close()

  # Clean up
  os.remove(local_path)
  return f"Uploaded to Gadi as {filename}"

@app.post('/process-data')
def process_data(data: DataInput):
  df = pd.DataFrame(data.dataframe)
  result = upload_to_gadi(df, data.filename)
  return {'message': result}


