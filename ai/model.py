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

    pred_flag = False

    def __init__(self, onnx_path: str, providers = ['CUDAExecutionProvider']):
        super().__init__()
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        self.detector = DetectionPredictor()
        self.session = onnxruntime.InferenceSession(onnx_path, providers=providers)

        self.metadata = self.session.get_modelmeta().custom_metadata_map
        self.input_name = self.session.get_inputs()[0].name

        self.output_names = [x.name for x in self.session.get_outputs()]
        # print(f"Meta Data   : {metadata}")

    def inference(self, origin_img):

        # 如果没有开始预测，就返回
        if self.pred_flag == False:
            return origin_img
        frame = origin_img.copy()
        
        img = self.detector.preprocess(frame)

        

       
        preds = self.session.run(self.output_names, {self.input_name: img})
        preds = self.detector.postprocess(torch.from_numpy(preds[0]), img, [origin_img])

        if len(preds) != 0:
            bbox_xyxy = preds[0][:, :4].numpy()
            bbox_xywh = self._xyxy2xywh(bbox_xyxy)
            cls_conf = preds[0][:, 4].numpy()
            cls_ids = preds[0][:, 5].numpy()
            self.notify_observers(ObserverData(None, ((bbox_xywh, cls_conf, cls_ids), origin_img)))
        return origin_img
    
    def _xyxy2xywh(self, xyxy):
        x1, y1, x2, y2 = xyxy[:, 0], xyxy[:, 1], xyxy[:, 2], xyxy[:, 3]
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        w = x2 - x1
        h = y2 - y1
        return np.stack([x, y, w, h], axis=-1)
    
