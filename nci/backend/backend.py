from nci.backend.Credentials import Credentials
from nci.backend.DirsGadi import DirsGadi
from nci.backend.utils import create_ssh_client
from nci.backend.utils import handle_nans
from nci.backend.utils import upload_to_gadi
from nci.backend.DataInput import DataInput
from nci.backend.JobRequest import JobRequest
from fastapi import FastAPI
import pandas as pd
import paramiko
import os
import time


c: Credentials = Credentials.__from_json__('nci/configs/credentials.json')
dg: DirsGadi = DirsGadi.__from_json__('nci/configs/dirs_gadi.json')
ssh = create_ssh_client(c, dg)
app = FastAPI()

# def submit_pbs_job(filename: str) -> str:
# 	script = f"""#!/bin/bash
# #PBS -l walltime=00:10:00,ncpus=1,mem=2GB
# #PBS -N job_{filename}
# #PBS -o {GADI_OUTPUT_DIR}/{filename}.out
# #PBS -e {GADI_OUTPUT_DIR}/{filename}.err

# cd {GADI_OUTPUT_DIR}
# module load python3
# python3 run_daesim.py {GADI_INPUT_DIR}/{filename} {GADI_OUTPUT_DIR}/{os.path.splitext(filename)[0]}_result.csv
# """

# 	jobfile = f"/tmp/job_{filename}.sh"
# 	with open(jobfile, "w") as f:
# 		f.write(script)

# 	remote_jobfile = f"{GADI_INPUT_DIR}/job_{filename}.sh"

# 	ssh = paramiko.SSHClient()
# 	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 	ssh.connect(GADI_HOST, username=GADI_USERNAME, key_filename=GADI_KEY_PATH)

# 	sftp = ssh.open_sftp()
# 	sftp.put(jobfile, remote_jobfile)
# 	sftp.close()

# 	stdin, stdout, stderr = ssh.exec_command(f"qsub {remote_jobfile}")
# 	job_output = stdout.read().decode().strip()
# 	ssh.close()

# 	return job_output

# ---- Endpoints ----
@app.post("/upload-to-gadi")
def upload_file(data: DataInput):
	print(data)
	df = pd.DataFrame(data.dataframe)
	df = handle_nans(df)
	remote_path = upload_to_gadi(ssh, dg, df, data.filename)
	return {"message": f"Uploaded {data.filename} to Gadi at {remote_path}"}

# @app.post("/submit-job")
# def submit_job(request: JobRequest):
# 	job_id = submit_pbs_job(request.filename)
# 	return {"message": f"PBS job submitted for {request.filename}", "job_id": job_id}
