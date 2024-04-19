from ai.model import YOLOV8
from Observers import SignImgWriter
# from Observers import ImageWriter, DataBaseWriter, DeepSortObserver, SignImgWriter
from face import FaceRecognition

def create_action_detection_model(pred_flag = True):
    yolo = YOLOV8("./ai/onnx/smart_model.onnx")
    yolo.pred_flag = pred_flag
    # yolo.register_observer(DeepSortObserver("./configs/deep_sort.yaml"))

    # , ImageWriter(), DataBaseWriter()

    return yolo

def create_FaceRecognition(minioClient):
    
    retinaface = FaceRecognition()
    retinaface.register_observer(SignImgWriter(minioClient))
    return retinaface