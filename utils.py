from datetime import datetime
import uuid
import cv2

def create_folder_name_by_date():
    now = datetime.now()
    folder_name = now.strftime(f"%Y%m%d")
    return folder_name


def create_unique_filename():
    filename = str(uuid.uuid4())
    return filename



def draw_bbox_with_text(img, bbox, text, font_scale, text_color, bg_color, thickness):
    x1, y1, x2, y2 = bbox

    # 绘制边界框
    #   print((x1, y1), (x2, y2), bg_color, thickness)
    cv2.rectangle(img, (x1, y1), (x2, y2), bg_color, thickness)

    # 计算文字位置
    text_pos = (x1, y1 - 5)

    # 在边界框上方绘制文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, text_pos, font, font_scale, text_color, thickness)

