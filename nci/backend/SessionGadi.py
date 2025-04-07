from nci.backend.Credentials import Credentials
from nci.backend.DirsGadi import DirsGadi
from dataclasses import dataclass
from dataclasses import field
from typing import Self
import paramiko


@dataclass(frozen=True)
class SessionGadi:
  creds       : Credentials
  dirs        : DirsGadi

  c = property(lambda s: s.creds)
  d = property(lambda s: s.dirs)

  def get_new_sftp_client(s: Self):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(s.creds.HOST, username=s.creds.USER, pkey=s.creds.PKEY)
    sftp = ssh.open_sftp()
    return sftp
  # sftp_client : paramiko.sftp_client.SFTPClient = field(init=False)

  # sftp_client = property()