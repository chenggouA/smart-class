
# 写入数据库
import os
from utils import *
from database.domain import HautActionRecord, HautCoordinates, get_session
from config import *
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

# 保存图片
class ImageWriter:
    imageSaveDir = imageSaveDir

    def update(self, data: ObserverData):

        _, origin_img = data.get_original()

        
        folderName = os.path.join(self.imageSaveDir, create_folder_name_by_date())
        os.makedirs(folderName, exist_ok=True)
        fileName = os.path.join(folderName, create_unique_filename() + ".jpg")
        cv2.imwrite(fileName, origin_img)

        return data.set_previous(fileName)

        

# 写入数据库
class DataBaseWriter:

    db_session = get_session()
    def update(self, data: ObserverData):

        preds, _ = data.get_original()
        fileName = data.get_previous()

        actionRecord = HautActionRecord(image_url=fileName, timestamp=datetime.now())
        self.db_session.add(actionRecord)
        self.db_session.commit()

        coordinates = []

        for item in preds[0].numpy():
            bbox = (int(item[0]), int(item[1]), int(item[2]), int(item[3]))
            coordinates.append(HautCoordinates(behavior_id = item[5] + 1, action_record_id = actionRecord.id, x1=bbox[0], y1=bbox[1], x2=bbox[2], y2=bbox[3]))
            # draw_bbox_with_text(origin_img, bbox, text, font_scale, text_color, class_color.get(item[5]), thickness)
        
        self.db_session.add_all(coordinates)
        self.db_session.commit()

        return data.set_previous(None)