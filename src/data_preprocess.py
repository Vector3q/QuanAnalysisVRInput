import json
import utils
import os
import argparse

# 需要添加以下数据

# 是否是海森堡错误
# 海森堡偏差

def extract_json_data(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'selectionSequence' in data:
        entries = data['selectionSequence']
        tech = data['inputtechnique']
        
        for entry in entries:
            entry['HeisenbergError'] = 0
            # entry['HeisenbergOffset'] = [0.0, 0.0, 0.0]
            if not entry['isCorrect']:
                if tech == "ControllerIntenSelect" or tech == "ControllerTracking":
                    intention_index = len(entry['historyCaches']) - 1
                    while intention_index >= 0:
                        if entry['historyCaches'][intention_index].get('confirmationValue', 0.0) == 0 and entry['historyCaches'][intention_index]['intendedObjectID'] != "null":
                            break
                        intention_index -= 1
                    if intention_index >= 0:
                        intention_obj = entry['historyCaches'][intention_index]['intendedObjectID']
                        target_obj = entry['targetPointID']
                        if (intention_obj is not None and 
                                target_obj is not None and 
                                intention_obj == target_obj):
                            entry['HeisenbergError'] = 1
                        
                elif tech == "BareHandIntenSelect" or tech == "BareHandTracking":
                    velocityDIs = [cache.get('velocityDI', 0) for cache in entry['historyCaches']]
                    peak_index = velocityDIs.index(max(velocityDIs))
                    stable_index = peak_index
                    while stable_index >= 0:
                        if velocityDIs[stable_index] <= 0.1 and entry['historyCaches'][stable_index]['intendedObjectID'] != "null":
                            break
                        stable_index -= 1
                    if stable_index >= 0:
                        stable_obj = entry['historyCaches'][stable_index]['intendedObjectID']
                        target_obj = entry['targetPointID']
                        if (stable_obj == target_obj):
                            entry['HeisenbergError'] = 1

            entry.pop('selectedPointID', None)
            entry.pop('targetPointID', None)
            entry.pop('targetPointPos', None)
            entry.pop('endPointInStart', None)
            entry.pop('endPointInEnd', None)
            entry.pop('historyCaches', None)
    
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
        json_file = extract_json_data(json_file)

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
        json_file = extract_json_data(json_file)

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

def save_data_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

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

    data_spacing_03, data_spacing_05, data_spacing_07 = load_jsons_s(f'../data\Heisenberg', full_name)
    data_radius_007, data_radius_014, data_radius_021 = load_jsons_r(f'../data\Heisenberg', full_name)

    print("the technology type is: ", full_name)
    print("len of the readin data for spacing: ", len(data_spacing_03), len(data_spacing_05), len(data_spacing_07))
    print("len of the readin data for radius: ", len(data_radius_007), len(data_radius_014), len(data_radius_021))

    if len(data_spacing_03) > 0:
        save_data_to_json(data_spacing_03, './output_json/' + full_name + '_spacing_03_data.json')
        print("the data has been saved into ", full_name + '_spacing_03_data.json')
    if len(data_spacing_05) > 0:
        save_data_to_json(data_spacing_05, './output_json/' + full_name + '_spacing_05_data.json')
        print("the data has been saved into ", full_name + '_spacing_05_data.json')
    if len(data_spacing_07) > 0:
        save_data_to_json(data_spacing_07, './output_json/' + full_name + '_spacing_07_data.json')
        print("the data has been saved into ", full_name + '_spacing_07_data.json')


    if len(data_radius_007) > 0:
        save_data_to_json(data_radius_007, './output_json/' + full_name + '_radius_007_data.json')
        print("the data has been saved into ", full_name + '_radius_007_data.json')
    if len(data_radius_014) > 0:
        save_data_to_json(data_radius_014, './output_json/' + full_name + '_radius_014_data.json')
        print("the data has been saved into ", full_name + '_radius_014_data.json')
    if len(data_radius_021) > 0:
        save_data_to_json(data_radius_021, './output_json/' + full_name + '_radius_021_data.json')
        print("the data has been saved into ", full_name + '_radius_021_data.json')

if __name__ == '__main__':
    main()
    