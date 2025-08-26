import json
from re import S
import utils
import os
import argparse
import math
import numpy as np

allcount = 0
topleft = 0
topright = 0
bottomleft = 0
bottomright = 0


bug_count = 0

def extract_json_data(input_path, technique):
    global allcount, topleft, topright, bottomleft, bottomright, bug_count


    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'selectionSequence' in data:
        
        

        entries = data['selectionSequence']
        tech = data['inputtechnique']

        for entry in entries:
            
            entry['HeisenbergError'] = 0
            entry['HeisenbergOffset'] = [0.0, 0.0, 0.0]
            last_frame = entry['historyCaches'][-1] if entry['historyCaches'] else None
            heisenberg_frame = None

            if tech == "ControllerIntenSelect" or tech == "ControllerTracking":
                intention_index = len(entry['historyCaches']) - 1
                while intention_index >= 0:
                    if entry['historyCaches'][intention_index].get('confirmationValue', 0.0) == 0 and entry['historyCaches'][intention_index]['intendedObjectID'] != "null":
                        break
                    intention_index -= 1
                if intention_index >= 0:
                    intention_obj = entry['historyCaches'][intention_index]['intendedObjectID']
                    target_obj = entry['targetPointID']
                    heisenberg_frame = entry['historyCaches'][intention_index]
                    if (intention_obj is not None and target_obj is not None and 
                            intention_obj == target_obj and not entry['isCorrect']):
                        entry['HeisenbergError'] = 1
                        
                        
            elif tech == "BareHandIntenSelect" or tech == "BareHandTracking":
                history_caches = entry['historyCaches']
                if len(entry['historyCaches']) == 0:
                    continue
                middle_index = len(history_caches) // 2

                velocityRots = [cache.get('velocityRot', 0) for cache in entry['historyCaches']]
                start_index = max(0, len(velocityRots) - 14)
                candidate_indices = [i for i in range(start_index, len(velocityRots)) if velocityRots[i] > 0.3]
                peak_index = min(candidate_indices) if candidate_indices else middle_index
                stable_index = peak_index
                
                while stable_index >= 0:
                    if velocityRots[stable_index] <= 0.001 and entry['historyCaches'][stable_index]['intendedObjectID'] != "null":
                        break
                    stable_index -= 1
                if stable_index >= 0:
                    stable_obj = entry['historyCaches'][stable_index]['intendedObjectID']
                    heisenberg_frame = entry['historyCaches'][stable_index]
                    target_obj = entry['targetPointID']
                    if (stable_obj == target_obj and not entry['isCorrect']):
                        entry['HeisenbergError'] = 1    
                else:
                    intended_id = history_caches[middle_index]['intendedObjectID']
                    heisenberg_frame = entry['historyCaches'][middle_index]
                    stable_index = middle_index
                    if intended_id == "null":
                        step = 1
                        found = False
                        while not found and step <= len(history_caches):
                            left_idx = middle_index - step
                            if left_idx >= 0 and history_caches[left_idx]['intendedObjectID'] != "null":
                                intended_id = history_caches[left_idx]['intendedObjectID']
                                found = True
                                break
                            right_idx = middle_index + step
                            if right_idx < len(history_caches) and history_caches[right_idx]['intendedObjectID'] != "null":
                                intended_id = history_caches[right_idx]['intendedObjectID']
                                found = True
                                break
                            step += 1

                    if intended_id == entry['targetPointID'] and not entry['isCorrect']: 
                        entry['HeisenbergError'] = 1


                # intended_id = history_caches[middle_index]['intendedObjectID']
                # heisenberg_frame = entry['historyCaches'][middle_index]
                # real_id = middle_index
                # if intended_id == "null":
                #     step = 1
                #     found = False
                #     while not found and step <= len(history_caches):
                #         left_idx = middle_index - step
                #         if left_idx >= 0 and history_caches[left_idx]['intendedObjectID'] != "null":
                #             intended_id = history_caches[left_idx]['intendedObjectID']
                #             real_id = left_idx
                #             found = True
                #             break
                #         right_idx = middle_index + step
                #         if right_idx < len(history_caches) and history_caches[right_idx]['intendedObjectID'] != "null":
                #             intended_id = history_caches[right_idx]['intendedObjectID']
                #             real_id = right_idx
                #             found = True
                #             break
                #         step += 1
                # if intended_id == entry['targetPointID'] and not entry['isCorrect']: 
                #     entry['HeisenbergError'] = 1

            entry['HeisenbergAngle'] = 0.0
            if heisenberg_frame and last_frame:
                
                if 'rayForward' in last_frame and 'rayForward' in heisenberg_frame and last_frame['rayForward'] and heisenberg_frame['rayForward']:
                    vec1 = last_frame['rayForward']
                    vec2 = heisenberg_frame['rayForward']
                    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
                    norm1 = math.sqrt(sum(v**2 for v in vec1))
                    norm2 = math.sqrt(sum(v**2 for v in vec2))
                    if norm1 == 0 or norm2 == 0:
                        angle_deg = 0.0
                    else:
                        cos_theta = dot_product / (norm1 * norm2)
                        cos_theta = max(min(cos_theta, 1.0), -1.0)
                        
                        angle_rad = math.acos(cos_theta)
                        angle_deg = math.degrees(angle_rad)
                    
                    entry['HeisenbergAngle'] = angle_deg
                    # print(f"Tech: {tech}, OffsetAngle: {entry['HeisenbergAngle']}")

                
                entry['HeisenbergOffset'] = [
                    last_frame['endPoint'][0] - heisenberg_frame['endPoint'][0],
                    last_frame['endPoint'][1] - heisenberg_frame['endPoint'][1],
                    last_frame['endPoint'][2] - heisenberg_frame['endPoint'][2]
                ]

                
                if entry['HeisenbergAngle'] == 0.0:
                    magnitude = np.sqrt(float(last_frame['endPoint'][0] - heisenberg_frame['endPoint'][0])**2 + float(last_frame['endPoint'][1] - heisenberg_frame['endPoint'][1])**2)
                    entry['HeisenbergAngle'] = (np.arctan(magnitude / 7.5) * (180 / np.pi))
            
                # print(f'tech should be: {technique} but is: {data["inputtechnique"]}')


                if tech != technique:
                    continue

                allcount += 1

                if entry['HeisenbergOffset'][0] > 0 and entry['HeisenbergOffset'][1] > 0:
                    topright += 1
                elif entry['HeisenbergOffset'][0] < 0 and entry['HeisenbergOffset'][1] > 0:
                    topleft += 1
                elif entry['HeisenbergOffset'][0] > 0 and entry['HeisenbergOffset'][1] < 0:
                    bottomright += 1
                elif entry['HeisenbergOffset'][0] < 0 and entry['HeisenbergOffset'][1] < 0:
                    bottomleft += 1

                if(entry['isCorrect'] == 0 and entry['selectedPointID'] == entry['targetPointID']):
                    bug_count += 1
                    print(f"path: {input_path}")



            entry.pop('HeisenbergOffset', None)
            entry.pop('selectedPointID', None)
            entry.pop('targetPointID', None)
            entry.pop('targetPointPos', None)
            entry.pop('endPointInStart', None)
            entry.pop('endPointInEnd', None)
            entry.pop('historyCaches', None)
        
        data.pop('studyname')
        data.pop('variable')

        data['clickDuration'] = sum([entry.get('clickDuration', 0) for entry in entries]) / len(entries)
        data['isCorrect'] = sum([entry.get('isCorrect', 0) for entry in entries]) / len(entries)
        data['HeisenbergError'] = sum([entry.get('HeisenbergError', 0) for entry in entries]) / len(entries)
        data['HeisenbergAngle'] = sum([entry.get('HeisenbergAngle', 0) for entry in entries]) / len(entries)
        data['EffectiveScore'] = (1/data['clickDuration']) * data['isCorrect']

        data.pop('selectionSequence')
    
    return data


def load_json_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def load_jsons_r_and_s(json_files_dir, technique=""):

    json_files = utils.get_all_json_files(json_files_dir)
    
    data_radius_007_spacing_03 = []
    data_radius_007_spacing_05 = []
    data_radius_007_spacing_07 = []
    data_radius_014_spacing_03 = []
    data_radius_014_spacing_05 = []
    data_radius_014_spacing_07 = []
    data_radius_021_spacing_03 = []
    data_radius_021_spacing_05 = []
    data_radius_021_spacing_07 = []

    for json_file in json_files:
        json_file = extract_json_data(json_file, technique)


        if technique != "":
            if json_file["inputtechnique"] != technique:
                continue
        
        if json_file["radius"] == 0.07 and json_file["spacing"] == 0.3:
            data_radius_007_spacing_03.append(json_file)
        elif json_file["radius"] == 0.07 and json_file["spacing"] == 0.5:
            data_radius_007_spacing_05.append(json_file)
        elif json_file["radius"] == 0.07 and json_file["spacing"] == 0.7:
            data_radius_007_spacing_07.append(json_file)
        elif json_file["radius"] == 0.14 and json_file["spacing"] == 0.3:
            data_radius_014_spacing_03.append(json_file)
        elif json_file["radius"] == 0.14 and json_file["spacing"] == 0.5:
            data_radius_014_spacing_05.append(json_file)
        elif json_file["radius"] == 0.14 and json_file["spacing"] == 0.7:
            data_radius_014_spacing_07.append(json_file)
        elif json_file["radius"] == 0.21 and json_file["spacing"] == 0.3:
            data_radius_021_spacing_03.append(json_file)
        elif json_file["radius"] == 0.21 and json_file["spacing"] == 0.5:
            data_radius_021_spacing_05.append(json_file)
        elif json_file["radius"] == 0.21 and json_file["spacing"] == 0.7:
            data_radius_021_spacing_07.append(json_file)

    return data_radius_007_spacing_03, data_radius_007_spacing_05, data_radius_007_spacing_07, data_radius_014_spacing_03, data_radius_014_spacing_05, data_radius_014_spacing_07, data_radius_021_spacing_03, data_radius_021_spacing_05, data_radius_021_spacing_07
def load_jsons_s(json_files_dir, technique=""):

    json_files = utils.get_all_json_files(json_files_dir)

    data_spacing_03 = []
    data_spacing_05 = []
    data_spacing_07 = []

    for json_file in json_files:
        json_file = extract_json_data(json_file)

        if technique != "":
            if json_file["inputtechnique"] != technique:
                continue

        if json_file["spacing"] == 0.3:
            data_spacing_03.append(json_file)
        elif json_file["spacing"] == 0.5:
            data_spacing_05.append(json_file)
        elif json_file["spacing"] == 0.7:
            data_spacing_07.append(json_file)

    return data_spacing_03, data_spacing_05, data_spacing_07



def load_jsons_r(json_files_dir, technique=""):
    json_files = utils.get_all_json_files(json_files_dir)

    data_radius_007 = []
    data_radius_014 = []
    data_radius_021 = []

    for json_file in json_files:
        json_file = extract_json_data(json_file, technique)


        if technique != "":
            if json_file["inputtechnique"] != technique:
                continue
        
        if json_file["radius"] == 0.07:
            data_radius_007.append(json_file)
        elif json_file["radius"] == 0.14:
            data_radius_014.append(json_file)
        elif json_file["radius"] == 0.21:
            data_radius_021.append(json_file)

    return data_radius_007, data_radius_014, data_radius_021

def main():
    FOLDER_ABBREVIATIONS = {
    'ControllerTracking': 'DC',
    'ControllerIntenSelect': 'SC',
    'BareHandTracking': 'DH',
    'BareHandIntenSelect': 'SH'
    }
    ABBREV_TO_FULL = {v: k for k, v in FOLDER_ABBREVIATIONS.items()}

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--tech', type=str, default='DC', help='the technique of the json files')

    args = parser.parse_args()
    full_name = ABBREV_TO_FULL.get(args.tech, args.tech)
    abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)

    # data_spacing_03, data_spacing_05, data_spacing_07 = load_jsons_s(f'../data\Heisenberg', full_name)
    # data_radius_007, data_radius_014, data_radius_021 = load_jsons_r(f'../data\Heisenberg_updated', full_name)
    data_radius_007, data_radius_014, data_radius_021 = load_jsons_r(f'../data\Heisenberg_updated', full_name)

    print("allcount: ", allcount)
    print(f"topright: {topright}, percentage: {topright/allcount}" )
    print(f"topleft: {topleft}, percentage: {topleft/allcount}" )
    print(f"bottomright: {bottomright}, percentage: {bottomright/allcount}" )
    print(f"bottomleft: {bottomleft}, percentage: {bottomleft/allcount}" )

    print(f"bug_count: {bug_count}" )
    
    print("the technology type is: ", full_name)
    # print("len of the readin data for spacing: ", len(data_spacing_03), len(data_spacing_05), len(data_spacing_07))
    print("len of the readin data for radius: ", len(data_radius_007), len(data_radius_014), len(data_radius_021))

if __name__ == '__main__':
    main()
    