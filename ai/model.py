from ultralytics.yolo.utils import ops
from ultralytics.yolo.data.dataloaders.stream_loaders import LoadPilAndNumpy
import onnx
import torch
import numpy as np
import onnxruntime
from ultralytics.yolo.engine.predictor import BasePredictor
from Observers import Observable, ObserverData


class DetectionPredictor(BasePredictor):

    def preprocess(self, img):
        img = LoadPilAndNumpy(img)._single_preprocess(img, False)
        img = img[np.newaxis, :].astype(np.float32)
        img = img / 255.
        return img

    def postprocess(self, preds, img, orig_imgs):
        preds = ops.non_max_suppression(
            preds,
            self.args.conf,
            self.args.iou,
            agnostic=self.args.agnostic_nms,
            max_det=self.args.max_det,
            classes=self.args.classes)

        results = []
        for i, pred in enumerate(preds):
            orig_img = orig_imgs[i] if isinstance(orig_imgs, list) else orig_imgs
            pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], orig_img.shape)
            results.append(pred)
        return results

class YOLOV8(Observable):
   
    conf, iou, agnostic_nms, max_det, classes = 0.25, 0.7, False, 300, None

    def __init__(self, onnx_path: str, providers = ['CUDAExecutionProvider']):
        super().__init__()
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        self.detector = DetectionPredictor()
        self.session = onnxruntime.InferenceSession(onnx_path, providers=providers)

        self.metadata = self.session.get_modelmeta().custom_metadata_map
        # print(f"Meta Data   : {metadata}")

    def inference(self, origin_img):
        frame = origin_img.copy()
        
        img = self.detector.preprocess(frame)

        input_names = self.session.get_inputs()[0]
        output_names = [x.name for x in self.session.get_outputs()]

       
        preds = self.session.run(output_names, {self.session.get_inputs()[0].name: img})
        preds = self.detector.postprocess(torch.from_numpy(preds[0]), img, [origin_img])

        if len(preds) != 0:
            self.notify_observers(ObserverData(None, (preds, origin_img)))
        return origin_img
    

# class Deepsort()