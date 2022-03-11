from classes import Source
from classes import MigrationTarget
from classes import Credentials
from classes import Workload
from classes import MountPoint
from classes import Migration
import os


def main(name):
    mounts = [MountPoint(MountPoint('h:\\', 120000000), MountPoint('d:\\', 240000000), MountPoint('c:\\', 100000000)), MountPoint()]
    source = Source(os.environ['SOURCE_USER'], os.environ['SOURCE_PASS'], ip='SOURCE_IP')
    credentials = Credentials(os.environ['MIG_USER'], os.environ['MIG_PASS'], os.environ['MIG_DOMAIN'])
    workload = Workload(os.environ['WORKLOAD_IP'], credentials, mounts)
    target = MigrationTarget(cloud_credentials=credentials, cloud_type=os.environ['CLOUD_TYPE'], target_vm=workload)
    selected_mounts = [MountPoint('h:\\', 120000000), MountPoint('d:\\', 240000000)]
    migration = Migration(selected_mounts, workload, target, 'not started')
    migration.run()


if __name__ == '__main__':
    main()
