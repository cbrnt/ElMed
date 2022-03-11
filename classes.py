import logging
from time import sleep

from loguru import logger
from typing import List


class MigrationErrors(Exception):
    def __init__(self, *args):
        logging.error(f'Error occurred during migration: {args}')


class Credentials:
    """Target cloud authorization credentials"""
    def __init__(self, username: str, password: str, domain: str):
        self.username = username
        self.password = password
        self.domain = domain


class MountPoint:
    """Mount point object.

    Size of disk vol_size must be set in bytes

    """
    def __init__(self, mount_point: str, vol_size: int):
        self.mount_point = mount_point
        self.vol_size = vol_size


class Workload:
    """Potential machine for migration"""
    def __init__(self, ip: str, credentials: Credentials, storage: List[MountPoint]):
        self.ip = ip
        self.credentials = credentials
        self.storage = storage


class Source:
    """Source machine parameters"""

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
    """Target for migration.

    cloud_type -- only 'aws', 'azure', 'vsphere', 'vcloud'
    target_vm -- attributes of target VM in cloud

    """
    def __init__(self, cloud_type: str,
                 cloud_credentials: Credentials, target_vm: Workload):
        assert cloud_type in ['aws', 'azure', 'vsphere', 'vcloud'], f'{cloud_type} is not supported'
        self.cloud_type = cloud_type
        self.cloud_credentials = cloud_credentials
        self.target_vm = target_vm


class Migration:
    def __init__(self, selected_mounts: List[MountPoint], migration_source: Workload,
                 migration_target: MigrationTarget, migration_state: str):
        assert migration_state in ['not started', 'running', 'error', 'success'], f'Unknown status: {migration_state}'
        self.selected_mounts = selected_mounts
        self.migration_source = migration_source
        self.migration_target = migration_target
        self.migration_state = migration_state

    def run(self):
        """Process migration

        - copy data only with selected mounts points;
        - not running migration without 'C:\' mount point
        """

        self.migration_target.target_vm = self.migration_source
        self.migration_target.target_vm.storage = self.selected_mounts

        if 'C:\\' in self.migration_target.target_vm.storage:
            print('Starting migration')
            try:
                self.migration_state = 'running'
                sleep(100)
                self.migration_state = 'success'
            except Exception as e:
                raise MigrationErrors(e)
        else:
            print("Mount points list isn't contain system disk. Can't start migration")

    def save_to_file(self):
        pass


