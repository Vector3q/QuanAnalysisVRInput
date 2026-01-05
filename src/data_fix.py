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
    row = 7
    column = 7

    object_data = {}

    for i in range(row):
        for j in range(column):
            target_position = ((j - 3) * target_spacing, (6 - i) * target_spacing)
            if username in ['FP1','FP2']:
                target_position = (target_position[0], target_position[1] + 0.3)

            idx = (i * row + j)
            object_name = "Object_" + str(idx)

            object_data[object_name] = target_position

    return object_data

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def find_closest_object_id(point, object_positions):

    min_distance = float('inf')
    closest_object_id = None

    for object_id, position in object_positions.items():
        distance = calculate_distance(point, position)
        if distance < min_distance:
            min_distance = distance
            closest_object_id = object_id

    return closest_object_id

def update_json_data(data, object_names_and_positions):
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
            
            # if not target_pos or not end_point_in_end:
            #     continue

            selected_point = (end_point_in_end[0], end_point_in_end[1])
            
            if technique in ['ControllerTracking', 'BareHandTracking']:
                radius = data.get('radius')
                if radius is not None:
                    distance_to_target = calculate_distance(selected_point, target_pos)
                    if distance_to_target <= radius:
                        seq['selectedPointID'] = target_id
                    else:
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
                            

            elif technique in ['ControllerIntenSelect', 'BareHandIntenSelect']:
                closest_object_id = find_closest_object_id(selected_point, object_names_and_positions)
                seq['selectedPointID'] = closest_object_id

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
                                        print(f"file {json_path} update.")
                                    else:
                                        print(f"Warning: file {json_path} no 'radius' or 'spacing' field, skip.")
                                except json.JSONDecodeError:
                                    print(f"Error: cannot parse JSON file {json_path}.")
                                except Exception as e:
                                    print(f"Error: handle file {json_path} occur error: {e}")
                            
if __name__ == '__main__':
    main()