from classes import Source
from classes import MigrationTarget
from classes import Credentials
from classes import Workload
from classes import MountPoint
import os


def main(name):
    mounts = [MountPoint(), MountPoint()]
    source = Source(os.environ['SOURCE_USER'], os.environ['SOURCE_PASS'], ip='SOURCE_IP')
    credentials = Credentials(os.environ['MIG_USER'], os.environ['MIG_PASS'], os.environ['MIG_DOMAIN'])
    workload = Workload(os.environ['WORKLOAD_IP'], credentials, mounts)
    migration = MigrationTarget(cloud_credentials=credentials, cloud_type=os.environ['CLOUD_TYPE'], target_vm=workload)


if __name__ == '__main__':
    main()
