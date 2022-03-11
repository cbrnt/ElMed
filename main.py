from classes import Source
from classes import MigrationTarget
from classes import Credentials
from classes import Workload
from classes import MountPoint
from classes import FileSystem
from classes import Migration
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", dest="path", required=True, help='point a JSON file with migration parameters')
    args = parser.parse_args()
    file = FileSystem(args.path)
    data = file.read()
    # gets data from JSON file
    # mounts
    mounts = []
    for key, value in data['mount_points'].items():
        mounts.append(MountPoint(key, value))
    source = Source(username=data['source']['username'],
                    password=data['source']['password'],
                    ip=data['source']['source_ip'])
    credentials = Credentials(data['credentials']['username'],
                              data['credentials']['password'],
                              data['credentials']['domain'])
    workload = Workload(ip=data['workload"']['ip'],
                        credentials=credentials, mounts=mounts)
    target = MigrationTarget(cloud_credentials=credentials,
                             cloud_type=data['migration']['cloud_type'],
                             target_vm=workload)
    migration = Migration(selected_mounts=data['selected_mounts'],
                          migration_source=source,
                          migration_target=target,
                          migration_state=data['migration']['migration_state'])

if __name__ == '__main__':
    main()
