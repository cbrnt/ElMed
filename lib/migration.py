import os
from time import sleep
from loguru import logger
from typing import List, Union
import json
from pathlib import Path

STORAGE = './migrations/'


class MigrationError(Exception):
    def __init__(self, *args):
        logger.error(f'Error occurred during migration: {args}')


class MountPointError(Exception):
    def __init__(self, *args):
        logger.error("Mount points list doesn't contain system disk. Can't start migration")


class FileError(Exception):
    def __init__(self, *args):
        logger.error(f'Error occurred during working with JSON: {args}')


class Credentials:
    """Target cloud authorization credentials."""

    def __init__(self, username: str, password: str, domain: str):
        self.username = username
        self.password = password
        self.domain = domain


class MountPoint:
    """Mount point object.

    Size of disk vol_size must be set in bytes

    """

    def __init__(self, mount_point: str, vol_size: int):
        self.mount_path = mount_point
        self.vol_size = vol_size


class Workload:
    """Potential machine for migration."""

    def __init__(self, ip: str, credentials: Credentials, storage: List[MountPoint]):
        self.ip = ip
        self.credentials = credentials
        self.storage = storage


class Source:
    """Source object for migration."""
    def __init__(self, username: str, password: str, ip: str):
        assert username is not None, logger.error('Username should not be empty')
        assert password is not None, logger.error('Password should not be empty')
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
        assert cloud_type in ['aws', 'azure', 'vsphere', 'vcloud'], f'{cloud_type} cloud type is not supported'
        self.cloud_type = cloud_type
        self.cloud_credentials = cloud_credentials
        self.target_vm = target_vm


class Migration:
    """Main migration object.

     Contains all essential data for starting migration.

     """
    def __init__(self, selected_mounts: List[MountPoint], migration_source: Workload,
                 migration_target: MigrationTarget, migration_state: str = 'not started'):
        assert migration_state in ['not started', 'running', 'error', 'success'], f'Unknown status: {migration_state}'
        self.selected_mounts = selected_mounts
        self.migration_source = migration_source
        self.migration_target = migration_target
        self.migration_state = migration_state

    def run(self):
        """Start migration process.

        - copy data only with selected mounts points;
        - not running migration without 'C:\' mount point

        """

        self.migration_target.target_vm = self.migration_source
        # this logic was a little bit unclear but anyway it is here
        self.migration_target.target_vm.storage = self.selected_mounts

        # check system mount
        found = False
        for mount in self.selected_mounts:
            if str.lower(mount.mount_path) == 'c:\\':
                found = True
                break
        if not found:
            raise MountPointError

        logger.info('Starting migration')
        try:
            self.migration_state = 'running'
            sleep(1)
            self.migration_state = 'success'
            logger.info('Migration finished successfully')
        except Exception as e:
            raise MigrationError(e)


class StateFile:
    """Keeping migration data as file.

    Using JSON format.
    Create file with name contains source IP address.
    Can't be duplicate file with the same source IP. In this case file will be rewritten.
    It helps to keep object unique.

    """

    def __init__(self, file):
        self.file = file

    @staticmethod
    def pack_json(
            source: Source,
            mounts: List[MountPoint],
            credentials_source_machine: Credentials,
            credentials_target_machine: Credentials,
            cloud_credentials: Credentials,
            workload_source_machine: Workload,
            workload_target_machine: Workload,
            target: MigrationTarget,
            migration: Migration
    ) -> dict:
        mounts_dict = {}
        for mount in mounts:
            mounts_dict[mount.mount_path] = mount.vol_size
        selected_mount_dict = {}
        for sel_mount in migration.selected_mounts:
            selected_mount_dict[sel_mount.mount_path] = sel_mount.vol_size
        json_dict = {
            "source": {
                "source_ip": source.ip,
                "username": source.username,
                "password": source.password
            },
            "source_machine": {
                "username": credentials_source_machine.username,
                "password": credentials_source_machine.password,
                "domain": credentials_source_machine.domain
            },
            "target_machine": {
                "username": credentials_target_machine.username,
                "password": credentials_target_machine.password,
                "domain": credentials_target_machine.domain
            },
            "cloud_credentials": {
                "username": cloud_credentials.username,
                "password": cloud_credentials.password,
                "domain": cloud_credentials.domain
            },
            "mount_points": mounts_dict,
            "workload": {
                "source_machine": {
                    "ip": workload_source_machine.ip
                },
                "target_machine": {
                    "ip": workload_target_machine.ip
                }
            },
            "migration_target": {
                "cloud_type": target.cloud_type,
            },
            "migration": {
                "selected_mounts": selected_mount_dict,
                "migration_state": migration.migration_state
            }
        }
        return json_dict

    def read(self) -> dict:
        """Gets data from migration file."""
        with open(self.file) as file:
            data = json.load(file)
        return data

    def write(self, data: dict):
        """Write data to JSON file."""
        with open(self.file, 'w') as file:
            return json.dump(data, file, indent=2)

    @staticmethod
    def list_files():
        return os.listdir('./migrations')

    @staticmethod
    def new(data):
        """Creates and save new migration object to file."""
        ip_name_list = str.split(data['source']['source_ip'], sep='.')
        file_name = STORAGE + '.'.join(ip_name_list) + '.json'
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=2)
        return file_name

    @staticmethod
    def remove(source_ip: Union[str, list]):
        """Remove file with object."""
        if isinstance(source_ip, list):
            file_name = []
            for line in source_ip:
                file_name.append('migrations/' + line + '.json')
            for file in file_name:
                path = Path(file)
                if path.exists():
                    os.remove(file)
                else:
                    return f"File {file} doesn't exist"
            return "Migrations deleted"
        else:
            file_name = 'migrations/' + source_ip + '.json'
            path = Path(file_name)
            if path.exists():
                os.remove(file_name)
                return "Migration deleted"
            else:
                return f"File {file_name} doesn't exist"


def build_migration(data: dict) -> Migration:
    """Create Migration object."""
    mounts = []
    for mount_path, vol_size in data['mount_points'].items():
        mounts.append(MountPoint(mount_path, vol_size))
    selected_mounts = []
    for mount_path, vol_size in data['migration']['selected_mounts'].items():
        selected_mounts.append(MountPoint(mount_path, vol_size))
    source = Source(data['source']['username'],
                    data['source']['password'],
                    data['source']['source_ip'])
    credentials_source_machine = Credentials(data['source_machine']['username'],
                                             data['source_machine']['password'],
                                             data['source_machine']['domain'])
    credentials_target_machine = Credentials(data['target_machine']['username'],
                                             data['target_machine']['password'],
                                             data['target_machine']['domain'])
    cloud_credentials = Credentials(data['cloud_credentials']['username'],
                                    data['cloud_credentials']['password'],
                                    data['cloud_credentials']['domain'])
    workload_source_machine = Workload(data['workload']['source_machine']['ip'],
                                       credentials_source_machine,
                                       mounts)
    workload_target_machine = Workload(data['workload']['target_machine']['ip'],
                                       credentials_target_machine,
                                       mounts)
    target = MigrationTarget(data['migration_target']['cloud_type'],
                             cloud_credentials,
                             workload_target_machine)
    migration = Migration(selected_mounts,
                          workload_source_machine,
                          target,
                          data['migration']['migration_state'])
    return migration
