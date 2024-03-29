
# 人脸识别的配置

import os
# 当前文件的完整路径
_current_file_path = os.path.abspath(__file__)

# 当前文件所在的目录
_current_dir = os.path.dirname(_current_file_path)

defaults = {
        # 是否绘制检测结果
        "drawImg": True,
        # 是否开始预测
        "pred_flag": True,
        
        #   retinaface训练完的权值路径
        
        "retinaface_model_path" : os.path.join(_current_dir, 'model_data/Retinaface_mobilenet0.25.pth'),
        
        #   retinaface所使用的主干网络，有mobilenet和resnet50
        
        "retinaface_backbone"   : "mobilenet",
        
        #   retinaface中只有得分大于置信度的预测框会被保留下来
        
        "confidence"            : 0.5,
        
        #   retinaface中非极大抑制所用到的nms_iou大小
        
        "nms_iou"               : 0.3,
        
        #   是否需要进行图像大小限制。
        #   输入图像大小会大幅度地影响FPS，想加快检测速度可以减少input_shape。
        #   开启后，会将输入图像的大小限制为input_shape。否则使用原图进行预测。
        #   会导致检测结果偏差，主干为resnet50不存在此问题。
        #   可根据输入图像的大小自行调整input_shape，注意为32的倍数，如[640, 640, 3]
        
        "retinaface_input_shape": [640, 640, 3],
        
        #   是否需要进行图像大小限制。
        
        "letterbox_image"       : True,
        
        
        #   facenet训练完的权值路径
        
        "facenet_model_path"    : os.path.join(_current_dir, 'model_data/facenet_mobilenet.pth'),
        
        #   facenet所使用的主干网络， mobilenet和inception_resnetv1
        
        "facenet_backbone"      : "mobilenet",
        
        #   facenet所使用到的输入图片大小
        
        "facenet_input_shape"   : [160, 160, 3],
        
        #   facenet所使用的人脸距离门限
        
        "facenet_threshold"      : 0.9,

        
        #   是否使用Cuda
        #   没有GPU可以设置成False
        
        "cuda"                  : True
    }