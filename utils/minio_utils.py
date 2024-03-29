
 
from minio.error import S3Error
import cv2
import io



def upload_cv2_image_to_minio(image, minio_client, bucket_name, object_name):
    is_success, im_buf_arr = cv2.imencode(".jpg", image)
    byte_im = im_buf_arr.tobytes()

    data = io.BytesIO(byte_im)

    try:
        minio_client.put_object(
            bucket_name, object_name, data, length=data.getbuffer().nbytes
        )
        print(f"成功提交图片到 {bucket_name}/{object_name}")
    except S3Error as err:
        print(err)



 