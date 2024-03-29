
saveFlag = False # 控制是否将数据写入数据库
imageSaveDir = "./images"

font_scale = .5
text_color = (255, 255, 35)  # 白色
thickness = 2
english_label_class_map = {
    0: 'tingjiang',
    1: 'niutou',
    2: 'kanshu',
    3: 'kanshouji',
    4: 'qili',
    5: 'chihe',
    6: 'pazhuozi',
    7: 'shuijiao',
    8: 'zoushen',
}

chinese_label_class_map = {
    0: '听讲',
    1: '扭头',
    2: '看书',
    3: '看手机',
    4: '起立',
    5: '吃喝',
    6: '趴桌子',
    7: '睡觉',
    8: '走神',
}

class_color = {
    0: (0, 0, 128),
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (0, 255, 0),
    4: (128, 0, 0),
    5: (255, 0, 0),
    6: (128, 128, 0),
    7: (128, 255, 0),
    8: (128, 128, 128)
}