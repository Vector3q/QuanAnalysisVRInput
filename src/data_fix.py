import json
from re import S
import utils
import os
import argparse
import math
import numpy as np



def get_object_names_and_positions(target_radius, target_spacing):
    """
    根据给定的半径和间距，生成物体的名称和位置的字典。
    
    Args:
        target_radius (float): 物体的半径。
        target_spacing (float): 物体之间的间距。
        
    Returns:
        dict: 一个字典，键是物体的名称（字符串），值是物体的位置（元组）。
    """
    # 假设行和列的值，这里从你提供的C#代码中推断
    row = 7
    column = 7

    object_data = {}

    for i in range(row):
        for j in range(column):
            # 计算物体的位置，这部分逻辑直接来自你提供的C#代码
            target_position = ((j - 3) * target_spacing, (6 - i) * target_spacing)

            # 计算物体的索引，然后生成名称
            idx = (i * row + j)
            object_name = "Object_" + str(idx)

            # 将物体的名称和位置添加到字典中
            object_data[object_name] = target_position

    return object_data

def calculate_distance(point1, point2):
    """
    计算两个二维点之间的欧几里得距离。

    Args:
        point1 (tuple): 第一个点的坐标，格式为 (x, y)。
        point2 (tuple): 第二个点的坐标，格式为 (x, y)。

    Returns:
        float: 两个点之间的距离。
    """
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def find_closest_object_id(point, object_positions):
    """
    根据给定的点，在物体位置字典中找到最近的物体ID。

    Args:
        point (tuple): 待匹配的二维点的坐标，格式为 (x, y)。
        object_positions (dict): 包含所有物体ID及其位置的字典。

    Returns:
        str: 最近的物体ID。
    """
    min_distance = float('inf')
    closest_object_id = None

    for object_id, position in object_positions.items():
        distance = calculate_distance(point, position)
        if distance < min_distance:
            min_distance = distance
            closest_object_id = object_id

    return closest_object_id

def main():
    
    TECHNIQUES = {
        'ControllerTracking': 'DC',
        'ControllerIntenSelect': 'SC',
        'BareHandTracking': 'DH',
        'BareHandIntenSelect': 'SH'
    }

    DATA_ROOT = os.path.join('..', 'data', 'Heisenberg')
    for item in os.listdir(DATA_ROOT):
        item_path = os.path.join(DATA_ROOT, item)
        if os.path.isdir(item_path) and item.startswith('FP'):
            subject = item
            for tech_full, tech_abbrev in TECHNIQUES.items():
                tech_path = os.path.join(item_path, tech_full, 'Study1')
                if os.path.exists(tech_path):
                    for filename in os.listdir(tech_path):
                        if filename.endswith('.json'):
                            json_path = os.path.join(tech_path, filename)
                            with open(json_path, 'r') as f:
                                data = json.load(f)
                                radius = data['radius']
                                spacing = data['spacing']
                                object_names_and_positions = get_object_names_and_positions(radius, spacing)
                                

    print(object_names_and_positions)
if __name__ == '__main__':
    main()