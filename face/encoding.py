import os
import numpy as np
import os, sys
sys.path.append(os.getcwd())
from face import FaceRecognition
'''
    对face_dataset 中的数据进行编码
'''

# 当前文件的完整路径
current_file_path = os.path.abspath(__file__)

# 当前文件所在的目录
current_dir = os.path.dirname(current_file_path)
model = FaceRecognition()

list_dir = os.listdir(os.path.join(current_dir, "face_dataset"))
image_paths = []
names = []
for name in list_dir:
    image_paths.append(os.path.join(current_dir, "face_dataset", name))
    names.append(name.split("_")[0])

import cv2
face_encodings = []
for img in image_paths:
    img = cv2.imread(img)

    boxes_conf_landms = model.get_boxes_conf_landms(img)

    if boxes_conf_landms is None:
        print("没有检测到有效的人脸")
        continue
    
    box, _ = model.get_maximum_box(boxes_conf_landms)
    

    _, calibration_imgs = model.get_face_images_pre_post_calibration(img, [box])

    face_encoding = model.get_face_encodings(calibration_imgs)[0]
    face_encodings.append(face_encoding)

np.save(os.path.join(current_dir, "model_data/{backbone}_face_encoding.npy".format(backbone=model.facenet_backbone)), face_encodings)
np.save(os.path.join(current_dir, "model_data/{backbone}_names.npy".format(backbone=model.facenet_backbone)), names)   

    


