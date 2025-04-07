from nci.backend.Credentials import Credentials
from nci.backend.DirsGadi import DirsGadi
from paramiko.client import SSHClient
from paramiko import AutoAddPolicy
import pandas as pd
import os

def create_ssh_client(creds: Credentials, dg: DirsGadi)->SSHClient:
  ssh = SSHClient()
  ssh.set_missing_host_key_policy(AutoAddPolicy())
  ssh.connect(creds.HOST, username=creds.USER, pkey=creds.PKEY)
  return ssh

def refresh_ssh_client_if_needed(ssh: SSHClient, creds: Credentials, dg: DirsGadi)->SSHClient:
  return ssh if ssh.get_transport() else create_ssh_client(creds, dg)

def handle_nans(df: pd.DataFrame) -> pd.DataFrame:
	df = df.copy()
	for col in df.columns:
		if pd.api.types.is_numeric_dtype(df[col]):
			df[col] = df[col].fillna(0)
		elif pd.api.types.is_bool_dtype(df[col]):
			df[col] = df[col].fillna(False)
		elif pd.api.types.is_datetime64_any_dtype(df[col]):
			df[col] = df[col].fillna(pd.Timestamp("1970-01-01"))
		else:
			df[col] = df[col].fillna("missing")
	return df

def upload_to_gadi(
  ssh: SSHClient,
	dg: DirsGadi,
  df: pd.DataFrame,
  filename: str
) -> str:
	
	local_path = f"/tmp/{filename}"
	remote_path = os.path.join(dg.input, filename)

	df.to_csv(local_path, index=False)

	sftp = ssh.open_sftp()
	# Ensure input directory exists
	remote_dir = os.path.dirname(remote_path)
	dirs = remote_dir.strip("/").split("/")
	current = "/"
	for folder in dirs:
		current = os.path.join(current, folder)
		try:
			sftp.chdir(current)
		except IOError:
			sftp.mkdir(current)
			sftp.chdir(current)

	sftp.put(local_path, remote_path)
	sftp.close()
	os.remove(local_path)
	return remote_path
