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
import io
from matplotlib import pyplot as plt
import base64
import matplotlib

matplotlib.use('Agg')


c: Credentials = Credentials.__from_json__('nci/configs/credentials.json')
dg: DirsGadi = DirsGadi.__from_json__('nci/configs/dirs_gadi.json')
ssh = create_ssh_client(c, dg)
app = FastAPI()

# ---- Endpoints ----
@app.post("/upload-to-gadi")
def upload_file(data: DataInput):
	df = pd.DataFrame(data.dataframe)
	df = handle_nans(df)
	remote_path = upload_to_gadi(ssh, dg, df, data.filename)
	return {"message": f"Uploaded {data.filename} to Gadi at {remote_path}"}

def generate_plot_base64(df: pd.DataFrame, x_col: str, y_col: str) -> str:
	fig, ax = plt.subplots()
	ax.plot(df[x_col], df[y_col], marker='o')
	ax.set_xlabel(x_col)
	ax.set_ylabel(y_col)
	ax.set_title(f'{y_col} vs {x_col}')
	ax.grid(True)
	buf = io.BytesIO()
	plt.savefig(buf, format='png')
	plt.close(fig)
	buf.seek(0)
	return base64.b64encode(buf.read()).decode("utf-8")

@app.get("/get-result-and-plot")
def get_result_and_plot(filename: str):
	job_name = os.path.splitext(filename)[0]
	remote_result = os.path.join(dg.output, f"{job_name}_result.csv")
	local_result = f"/tmp/{job_name}_result.csv"

	ssh = create_ssh_client(c, dg)
	sftp = ssh.open_sftp()
	try:
		sftp.get(remote_result, local_result)
	except FileNotFoundError:
		sftp.close()
		ssh.close()
		return {"error": f"Output file not found for {filename}"}

	sftp.close()
	df = pd.read_csv(local_result)
	cols = df.columns.tolist()
	if len(cols) < 2:
		return {"error": "Not enough columns to plot."}

	plot_base64 = generate_plot_base64(df, cols[0], cols[5])
	return {
		"message": f"✅ Loaded result for {filename}",
		"plot_image_base64": plot_base64,
		"data": df.to_dict(orient="records")
	}
# @app.post("/submit-job")
# def submit_job(request: JobRequest):
# 	job_id = submit_pbs_job(request.filename)
# 	return {"message": f"PBS job submitted for {request.filename}", "job_id": job_id}
