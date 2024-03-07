from datetime import date, datetime

from paramiko import AutoAddPolicy, SSHClient


class Client:

    # "sbatch $HOME/mycostreams/slurm-uploader/scripts/run-basic.sh {date_str}"
    COMMAND = 'sbatch --wrap "echo {date_str}" --partition staging'

    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        connection_url: str,
        port: int = 22,
    ):
        self.username = username
        self.password = password
        self.hostname = host
        self.port = port
        self.connection_url = connection_url

    def __enter__(self):
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())

        self.ssh_client.connect(
            self.hostname,
            self.port,
            self.username,
            self.password,
        )

    def __exit__(self, *args, **kwargs):
        self.ssh_client.close()

    def submit_job(self, date: date | datetime):
        self.COMMAND.format(date_str=date.strftime("%Y%m%d"))

        _, stdout, _ = self.ssh_client.exec_command(
            self.COMMAND,
            environment={"CONNECTION_URL": self.connection_url},
        )
        return stdout.read().decode()
