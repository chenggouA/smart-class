from configs import minio_cfg
from minio import Minio
# 获取minio客户端
def get_minio_client():
    minioClient = Minio(minio_cfg['endpoint'],
                    access_key=minio_cfg['root_name'],
                    secret_key=minio_cfg['root_password'],
                    secure=False)
    
    return minioClient