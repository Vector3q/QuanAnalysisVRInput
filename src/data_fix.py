import json
from re import S
import utils
import os
import argparse
import math
import numpy as np

TECHNIQUES = {
    'ControllerTracking': 'DC',
    'ControllerIntenSelect': 'SC',
    'BareHandTracking': 'DH',
    'BareHandIntenSelect': 'SH'
}
DATA_ROOT = os.path.join('..', 'data', 'Heisenberg')
OUTPUT_ROOT = os.path.join('..', 'data', 'Heisenberg_updated')

def get_object_names_and_positions(username, target_radius, target_spacing):
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
            if username in ['FP1','FP2']:
                target_position = (target_position[0], target_position[1] + 0.3)

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

def update_json_data(data, object_names_and_positions):
    """
    更新 JSON 数据，根据输入技术采用不同的逻辑。

    Args:
        data (dict): 从 JSON 文件加载的字典数据。
        object_names_and_positions (dict): 包含物体ID和位置的字典。
    """
    technique = data.get('inputtechnique', '')
    username = data.get('username','')

    if 'selectionSequence' in data:
        for seq in data['selectionSequence']:
            target_pos_list = seq.get('targetPointPos')
            if target_pos_list and len(target_pos_list) >= 2:
                target_point_2d = (target_pos_list[0], target_pos_list[1])
                
                new_target_id = find_closest_object_id(target_point_2d, object_names_and_positions)
                seq['targetPointID'] = new_target_id

            target_id = seq.get('targetPointID')
            target_pos = object_names_and_positions.get(target_id)
            end_point_in_end = seq.get('endPointInEnd')
            
            # 确保关键数据存在
            # if not target_pos or not end_point_in_end:
            #     continue

            # 提取 x 和 y 坐标
            selected_point = (end_point_in_end[0], end_point_in_end[1])
            
            # D 开头的方法：检查落点是否在目标圆内
            if technique in ['ControllerTracking', 'BareHandTracking']:
                radius = data.get('radius')
                if radius is not None:
                    # 计算落点到目标中心的距离
                    distance_to_target = calculate_distance(selected_point, target_pos)
                    # 如果距离小于半径，则选中目标，否则未选中
                    if distance_to_target <= radius:
                        seq['selectedPointID'] = target_id
                    else:
                        # 如果未选中，则根据最近原则找到落点对应的ID
                        seq['selectedPointID'] = "null" 

                    # for idx, cache in enumerate(selection['historyCaches']):
                    #         intended = cache['intendedObjectID']
                    #         is_correct = int(intended == selection['targetPointID'])
                    #         records.append({
                    #             'user': data['username'],
                    #             'relative_position': idx/(lens-1),
                    #             'is_correct': is_correct
                    #         })

                    if 'historyCaches' in seq:
                        cache_len = len(seq['historyCaches'])
                        for idx, cache in enumerate(seq['historyCaches']):
                            if 'endPoint' in cache and len(cache['endPoint']) >= 2:
                                intended_point = (cache['endPoint'][0], cache['endPoint'][1])
                                candidate_object = find_closest_object_id(intended_point, object_names_and_positions)
                                cache['cloestObjectID'] = candidate_object
                                cache['relativeTime'] = idx/(cache_len-1)
                                candidate_object_pos = object_names_and_positions.get(candidate_object)
                                distance_to_candidate = calculate_distance(intended_point, candidate_object_pos)
                                cache['cloestDistance'] = distance_to_candidate
                                cache['intended_pos'] = intended_point
                                cache['cloest_pos'] = candidate_object_pos
                                if distance_to_candidate <= radius:
                                    cache['intendedObjectID'] = candidate_object
                                else:
                                    cache['intendedObjectID'] = "null"
                            

            # S 开头的方法：距离哪个最近就选哪个
            elif technique in ['ControllerIntenSelect', 'BareHandIntenSelect']:
                # 找到离落点最近的物体ID
                closest_object_id = find_closest_object_id(selected_point, object_names_and_positions)
                seq['selectedPointID'] = closest_object_id

                # 更新 historyCaches 里的 intendedObjectID
                if 'historyCaches' in seq:
                    cache_len = len(seq['historyCaches'])
                    for idx, cache in enumerate(seq['historyCaches']):
                        if 'endPoint' in cache and len(cache['endPoint']) >= 2:
                            intended_point = (cache['endPoint'][0], cache['endPoint'][1])
                            cache['intendedObjectID'] = find_closest_object_id(intended_point, object_names_and_positions)
                            cache['relativeTime'] = idx/(cache_len-1)
    return data

def main():
    for item in os.listdir(DATA_ROOT):
        item_path = os.path.join(DATA_ROOT, item)
        if os.path.isdir(item_path) and item.startswith('FP'):
            for tech_full, tech_abbrev in TECHNIQUES.items():
                tech_path = os.path.join(item_path, tech_full, 'Study1')
                if os.path.exists(tech_path):
                    for filename in os.listdir(tech_path):
                        if filename.endswith('.json'):
                            json_path = os.path.join(tech_path, filename)

                            relative_path = os.path.relpath(json_path, DATA_ROOT)
                            output_path = os.path.join(OUTPUT_ROOT, relative_path)
                            output_dir = os.path.dirname(output_path)

                            if not os.path.exists(output_dir):
                                os.makedirs(output_dir)

                            with open(json_path, 'r') as f:
                                try:
                                    data = json.load(f)
                                    if 'radius' in data and 'spacing' in data:
                                        radius = data['radius']
                                        spacing = data['spacing']
                                        username = data['username']
                                        object_names_and_positions = get_object_names_and_positions(username, radius, spacing)

                                        updated_data = update_json_data(data, object_names_and_positions)

                                        with open(output_path, 'w') as out_f:
                                            json.dump(updated_data, out_f, indent=2)
                                        print(f"文件 {json_path} 已成功更新。")
                                    else:
                                        print(f"警告：文件 {json_path} 缺少 'radius' 或 'spacing' 字段，跳过。")
                                except json.JSONDecodeError:
                                    print(f"错误：无法解析 JSON 文件 {json_path}。")
                                except Exception as e:
                                    print(f"处理文件 {json_path} 时发生错误：{e}")
                            
if __name__ == '__main__':
    main()