from time import sleep

from loguru import logger
from typing import List


class Credentials:
    """

    todo add comments
    """
    def __init__(self, username: str, password: str, domain: str):
        self.username = username
        self.password = password
        self.domain = domain


class MountPoint:
    def __init__(self, mount_point: str, vol_size: int):
        self.mount_point = ''
        self.vol_size = 0


class Workload:
    def __init__(self, ip: str, credentials: Credentials, storage: List[MountPoint]):
        self.ip = ip
        self.credentials = credentials
        self.storage = storage


class Source:

    def __init__(self, username: str, password: str, ip: str):
        # todo add logging to file via loguru
        assert username is not None, 'Username should not be empty'
        assert password is not None, 'Password should not be empty'
        # todo add ip restriction
        assert ip is not None, 'IP should not be empty'
        self.username = username
        self.password = password
        self.ip = ip


class MigrationTarget:
    def __init__(
            self,
            cloud_type: str,
            cloud_credentials: Credentials,
            target_vm: Workload
    ):
        assert cloud_type in ['aws', 'azure', 'vsphere', 'vcloud'], f'{cloud_type} is not supported'
        self.cloud_type = cloud_type
        self.cloud_credentials = cloud_credentials
        self.target_vm = target_vm


class Migration:
    def __init__(self, selected_mounts: MountPoint, source: Workload):
        pass

    def run(self):
        sleep(100)



