
# 写入数据库
import os
from utils.utils import *
from database.domain import HautActionRecord, HautCoordinates, get_session
from configs.config import *
from deep_sort import build_tracker
from utils.parser import get_config
import warnings
import numpy as np  
import torch
class ObserverData:
    def __init__(self, previous, original):
        self.previous = previous
        self.original = original

    def set_previous(self, previous):
        self.previous = previous
        return self

    def set_original(self, original):
        self.original = original
        return self

    def get_previous(self):
        return self.previous

    def get_original(self):
        return self.original
        
        
# 观察者模式
class Observable:
    
    def __init__(self):
        self.observers = []

    def register_observer(self, *observers):
        for observer in observers:
            self.observers.append(observer)
    
    def notify_observers(self, data: ObserverData):
        for observer in self.observers:
            observer.update(data)


class DeepSortObserver:
    cfg = get_config()

    def __init__(self, config_deepsort):

        use_cuda = torch.cuda.is_available()

        if not use_cuda:
            warnings.warn("Running in cpu mode which maybe very slow!", UserWarning)
        self.cfg.merge_from_file(config_deepsort)
        self.deepsort = build_tracker(self.cfg, use_cuda=use_cuda)
        self.cls_dict = {}
    

    def update(self, data: ObserverData):
        (bbox_xywh, cls_conf, cls_ids), ori_im = data.get_original()
        outputs = self.deepsort.update(bbox_xywh, cls_conf, cls_ids, ori_im)
        
        results = []

        for item in outputs:
            bbox_xyxy = item[:4]
            identities = item[4]
            cls_ids = item[5]
            # ori_im = draw_boxes(ori_im, bbox_xyxy, identities)
            
            if self.cls_dict.get(identities, -1) == -1 or self.cls_dict.get(identities) != cls_ids:
                self.cls_dict[identities] = cls_ids
                results.append((bbox_xyxy, cls_ids))     

        return data.set_previous(results)
        
    

# 保存图片
class ImageWriter:

    imageSaveDir = imageSaveDir

    def update(self, data: ObserverData):

        _, origin_img = data.get_original()
        previous = data.get_previous()
        if len(previous) == 0:
            return data.set_previous(None)
        
        folderName = os.path.join(self.imageSaveDir, create_folder_name_by_date())
        os.makedirs(folderName, exist_ok=True)
        fileName = os.path.join(folderName, create_unique_filename() + ".jpg")
        cv2.imwrite(fileName, origin_img)

        return data.set_previous(fileName).set_original(previous)

        

# 写入数据库
class DataBaseWriter:

    db_session = get_session()
    def update(self, data: ObserverData):

        fileName = data.get_previous()
        if fileName == None:
            return data.set_previous(None)

        items = data.get_original()
        
        

        actionRecord = HautActionRecord(image_url=fileName, timestamp=datetime.now())
        self.db_session.add(actionRecord)
        self.db_session.commit()

        coordinates = []

        for bbox, cls_ids in items:

            coordinates.append(HautCoordinates(behavior_id = cls_ids + 1, action_record_id = actionRecord.id, x1=bbox[0], y1=bbox[1], x2=bbox[2], y2=bbox[3]))
            # draw_bbox_with_text(origin_img, bbox, text, font_scale, text_color, class_color.get(item[5]), thickness)
        
        self.db_session.add_all(coordinates)
        self.db_session.commit()

        return data.set_previous(None)
    


class SignImgWriter():
    db_session = get_session()