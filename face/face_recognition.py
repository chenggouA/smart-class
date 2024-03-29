import time

import cv2
import numpy as np
import torch
import torch.nn as nn

from tqdm import tqdm
from PIL import Image
from face.nets_facenet.facenet import Facenet
from face.nets_retinaface.retinaface import RetinaFace
from face.utils.anchors import Anchors
from face.utils.config import cfg_mnet, cfg_re50
from face.utils.utils import (Alignment_1, compare_faces, letterbox_image,
                         preprocess_input)
from face.utils.utils_bbox import (decode, decode_landm, non_max_suppression,
                              retinaface_correct_boxes)
from face.config import defaults
import os
# 当前文件的完整路径
current_file_path = os.path.abspath(__file__)

# 当前文件所在的目录
current_dir = os.path.dirname(current_file_path)


#   一定注意backbone和model_path的对应。
#   在更换facenet_model后，
#   一定要注意重新编码人脸。

class FaceRecognition:
    #   初始化Retinaface
    def __init__(self, encoding=0, **kwargs):
        super().__init__()
        self.__dict__.update(defaults)
        for name, value in kwargs.items():
            setattr(self, name, value)

        
        #   不同主干网络的config信息
        
        if self.retinaface_backbone == "mobilenet":
            self.cfg = cfg_mnet
        else:
            self.cfg = cfg_re50

        
        #   先验框的生成
        
        self.anchors = Anchors(self.cfg, image_size=(self.retinaface_input_shape[0], self.retinaface_input_shape[1])).get_anchors()
        self.generate()

        try:
            self.known_face_encodings = np.load(os.path.join(current_dir, "model_data/{backbone}_face_encoding.npy".format(backbone=self.facenet_backbone)))
            self.known_face_names     = np.load(os.path.join(current_dir, "model_data/{backbone}_names.npy".format(backbone=self.facenet_backbone)))
        except:
            if not encoding:
                print("载入已有人脸特征失败，请检查model_data下面是否生成了相关的人脸特征文件。")
            pass
    
    #   获得所有的分类
    
    def generate(self):
        
        #   载入模型与权值
        
        self.net        = RetinaFace(cfg=self.cfg, phase='eval', pre_train=False).eval()
        self.facenet    = Facenet(backbone=self.facenet_backbone, mode="predict").eval()
        device          = torch.device('cuda' if self.cuda else 'cpu')

        print('Loading weights into state dict...')
        state_dict = torch.load(self.retinaface_model_path, map_location=device)
        self.net.load_state_dict(state_dict)

        state_dict = torch.load(self.facenet_model_path, map_location=device)
        self.facenet.load_state_dict(state_dict, strict=False)

        if self.cuda:
            self.net = nn.DataParallel(self.net)
            self.net = self.net.cuda()

            self.facenet = nn.DataParallel(self.facenet)
            self.facenet = self.facenet.cuda()
        print('Finished!')

    # 获取识别到的人脸图像和矫正过的人脸图像
    def get_face_images_pre_post_calibration(self, old_image, boxes_conf_landms):
        crop_imgs = []
        calibration_imgs = []
        for boxes_conf_landm in boxes_conf_landms:
            #   图像截取
            boxes_conf_landm    = np.maximum(boxes_conf_landm, 0)
            crop_img            = np.array(old_image)[int(boxes_conf_landm[1]):int(boxes_conf_landm[3]), int(boxes_conf_landm[0]):int(boxes_conf_landm[2])]
            landmark            = np.reshape(boxes_conf_landm[5:],(5,2)) - np.array([int(boxes_conf_landm[0]),int(boxes_conf_landm[1])])
            calibration_img, _         = Alignment_1(crop_img, landmark)
            crop_imgs.append(crop_img)
            calibration_imgs.append(calibration_img)
        return crop_imgs, calibration_imgs

    # 获取人脸的识别框
    def get_boxes_conf_landms(self, old_image):
        #   检测图片
        #   对输入图像进行一个备份，后面用于绘图
        
        image   = old_image.copy()
        
        #   把图像转换成numpy的形式
        
        image       = np.array(image, np.float32)

        
        #   Retinaface检测部分-开始
        
        
        #   计算输入图片的高和宽
        
        im_height, im_width, _ = np.shape(image)
        
        #   计算scale，用于将获得的预测框转换成原图的高宽
        
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]

        #---------------------------------------------------------#
        #   letterbox_image可以给图像增加灰条，实现不失真的resize
        #---------------------------------------------------------#
        if self.letterbox_image:
            image = letterbox_image(image, [self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
            anchors = self.anchors
        else:
            anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()

        
        #   将处理完的图片传入Retinaface网络当中进行预测
        
        with torch.no_grad():
            #-----------------------------------------------------------#
            #   图片预处理，归一化。
            #-----------------------------------------------------------#
            image = torch.from_numpy(preprocess_input(image).transpose(2, 0, 1)).unsqueeze(0).type(torch.FloatTensor)

            if self.cuda:
                anchors = anchors.cuda()
                image   = image.cuda()

            #---------------------------------------------------------#
            #   传入网络进行预测
            #---------------------------------------------------------#
            loc, conf, landms = self.net(image)
            
            #   Retinaface网络的解码，最终我们会获得预测框
            #   将预测结果进行解码和非极大抑制
            
            boxes   = decode(loc.data.squeeze(0), anchors, self.cfg['variance'])

            conf    = conf.data.squeeze(0)[:, 1:2]
            
            landms  = decode_landm(landms.data.squeeze(0), anchors, self.cfg['variance'])
            
            #-----------------------------------------------------------#
            #   对人脸检测结果进行堆叠
            #-----------------------------------------------------------#
            boxes_conf_landms = torch.cat([boxes, conf, landms], -1)
            boxes_conf_landms = non_max_suppression(boxes_conf_landms, self.confidence)
        
            
            #   如果没有预测框则返回原图
            
            if len(boxes_conf_landms) <= 0:
                return None

            #---------------------------------------------------------#
            #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
            #---------------------------------------------------------#
            if self.letterbox_image:
                boxes_conf_landms = retinaface_correct_boxes(boxes_conf_landms, \
                    np.array([self.retinaface_input_shape[0], self.retinaface_input_shape[1]]), np.array([im_height, im_width]))

            boxes_conf_landms[:, :4] = boxes_conf_landms[:, :4] * scale
            boxes_conf_landms[:, 5:] = boxes_conf_landms[:, 5:] * scale_for_landmarks

        
        #   Retinaface检测部分-结束
            
        return boxes_conf_landms
    
    # 获取最大的识别框
    def get_maximum_box(self, boxes_conf_landms):
        #  获取最大的人脸
        best_face_location  = None
        biggest_area        = 0
        for result in boxes_conf_landms:
            left, top, right, bottom = result[0:4]

            w = right - left
            h = bottom - top
            if w * h > biggest_area:
                biggest_area = w * h
                best_face_location = result
        return best_face_location, biggest_area
        
    # 编码人脸
    def get_face_encodings(self, calibration_imgs):
        face_encodings = []
        for crop_img in calibration_imgs:
            #   人脸编码
            crop_img = np.array(letterbox_image(np.uint8(crop_img),(self.facenet_input_shape[1],self.facenet_input_shape[0])))/255
            crop_img = np.expand_dims(crop_img.transpose(2, 0, 1),0)
            with torch.no_grad():
                crop_img = torch.from_numpy(crop_img).type(torch.FloatTensor)
                if self.cuda:
                    crop_img = crop_img.cuda()

                #   利用facenet_model计算长度为128特征向量
                face_encoding = self.facenet(crop_img)[0].cpu().numpy()
                face_encodings.append(face_encoding)

        return face_encodings

    # 获取人脸信息
    def get_face_info(self, face_encodings):
        face_names = []
        for face_encoding in face_encodings:
            #   取出一张脸并与数据库中所有的人脸进行对比，计算得分
            matches, face_distances = compare_faces(self.known_face_encodings, face_encoding, tolerance = self.facenet_threshold)
            name = "Unknown"
            #   取出这个最近人脸的评分
            #   取出当前输入进来的人脸，最接近的已知人脸的序号
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]: 
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        return face_names


    # 绘制预测框和人脸关键点以及姓名信息
    def draw(self, old_image, face_names, boxes_conf_landms):
        for b, name in zip(boxes_conf_landms, face_names):
            text = "{:.4f}".format(b[4])
            b = list(map(int, b))
            
            #   b[0]-b[3]为人脸框的坐标，b[4]为得分
            
            cv2.rectangle(old_image, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
            cx = b[0]
            cy = b[1] + 12
            cv2.putText(old_image, text, (cx, cy),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

            
            #   b[5]-b[14]为人脸关键点的坐标
            
            cv2.circle(old_image, (b[5], b[6]), 1, (0, 0, 255), 4)
            cv2.circle(old_image, (b[7], b[8]), 1, (0, 255, 255), 4)
            cv2.circle(old_image, (b[9], b[10]), 1, (255, 0, 255), 4)
            cv2.circle(old_image, (b[11], b[12]), 1, (0, 255, 0), 4)
            cv2.circle(old_image, (b[13], b[14]), 1, (255, 0, 0), 4)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(old_image, name, (b[0] , b[3] - 15), font, 0.75, (255, 255, 255), 2) 
            #   cv2不能写中文，加上这段可以，但是检测速度会有一定的下降。
            #   如果不是必须，可以换成cv2只显示英文。
            # old_image = cv2ImgAddText(old_image, name, b[0]+5 , b[3] - 25)
    
    def detect_image(self, old_image):
        
        boxes_conf_landms = self.get_boxes_conf_landms(old_image)

        if boxes_conf_landms is None:
            return old_image   
       
        _, calibration_imgs = self.get_face_images_pre_post_calibration(old_image, boxes_conf_landms)
        
        # 获取人脸编码
        face_encodings = self.get_face_encodings(calibration_imgs)

        # 人脸特征比对
        face_names = self.get_face_info(face_encodings)
        
        # 绘制
        if self.drawImg:
            self.draw(old_image, face_names, boxes_conf_landms)
        return old_image
    
    
    def preprocess(self, frame):
        # 格式转变，BGRtoRGB
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        return frame
        

    def inference(self, ori_img):
        if self.pred_flag == False:
            return ori_img
        
        frame = self.preprocess(ori_img)
        # 预测
        frame = np.array(self.detect_image(frame))

        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
   

    