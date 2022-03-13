from loguru import logger
from lib.migration import StateFile
from lib.migration import MountPoint
from lib.migration import Source
from lib.migration import Credentials
from lib.migration import MigrationTarget
from lib.migration import Migration
from lib.migration import Workload
import argparse


def main():
    parser = argparse.ArgumentParser(description="Running migration process. Use --data parameter to point state file")
    parser.add_argument("--data", dest="path", required=True, help='point a JSON file with migration parameters')
    args = parser.parse_args()

    state_file = StateFile(args.path)
    data = state_file.read()
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
    if migration.migration_state != 'running':
        migration.run()
    else:
        logger.warning("Migration is already in progress! Can't start another one")

    # changing 'cloud_type'
    target.cloud_type = 'azure'

    # save form JSON
    json_to_file = state_file.pack_json(
        source=source,
        mounts=mounts,
        credentials_source_machine=credentials_source_machine,
        credentials_target_machine=credentials_target_machine,
        cloud_credentials=cloud_credentials,
        workload_source_machine=workload_source_machine,
        workload_target_machine=workload_target_machine,
        target=target,
        migration=migration
    )
    result = state_file.write(json_to_file)

    # create migration with new source IP and target IP
    source.ip = "101.10.14.192"
    target.target_vm.ip = '9.9.9.9'
    new_migration_json = StateFile.pack_json(
        source=source,
        mounts=mounts,
        credentials_source_machine=credentials_source_machine,
        credentials_target_machine=credentials_target_machine,
        cloud_credentials=cloud_credentials,
        workload_source_machine=workload_source_machine,
        workload_target_machine=workload_target_machine,
        target=target,
        migration=migration
    )
    new_object = StateFile.new(new_migration_json)
    # Remove old migration object
    # StateFile.remove("101.10.14.92")


if __name__ == '__main__':
    main()
