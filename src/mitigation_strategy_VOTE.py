import os
import argparse
import json
import utils


from collections import defaultdict, Counter

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

    fp_range = utils.fp_test
        
    data_folders = [
        os.path.join('..', 'data', 'Heisenberg', f'FP{i}', full_name, 'Study1') 
        for i in fp_range
    ]
    
    click_count = 0
    records_with_target = 0
    records_with_same_history = 0
    total_error_count = 0
    heisenberg_error_count = 0
    total_VOTE_eror_count = 0
    tech_name = full_name

    for data_folder in data_folders:
        # print(f"\nAnalyzing file folder: {data_folder}")

        for filename in os.listdir(data_folder):
            if filename.endswith('.json'):
                json_path = os.path.join(data_folder, filename)
                
                with open(json_path, 'r') as f:
                    data = json.load(f)

                selection_sequence = data['selectionSequence']
                total_selections = len(selection_sequence)
                start_index = int(total_selections * 0.2)
                selection_sequence = selection_sequence[start_index:]  

                radius = data['radius']
                spacing = data['spacing']

                tech = data['inputtechnique']

                for selection in selection_sequence:
                    
                    if selection['clickDuration'] < 0.05:
                        continue
                    
                    click_count += 1

                    intended_objects = [cache['intendedObjectID'] for cache in selection['historyCaches'] 
                    if 'intendedObjectID' in cache and cache['intendedObjectID'] != "null"]
                    
                    target_id = selection['targetPointID']
                    if target_id in intended_objects:
                        records_with_target += 1

                    all_caches_same = True
                    first_id = None
                    for cache in selection['historyCaches']:
                        if 'intendedObjectID' not in cache or cache['intendedObjectID'] == "null":
                            all_caches_same = False
                            break
                        if first_id is None:
                            first_id = cache['intendedObjectID']
                        elif cache['intendedObjectID'] != first_id:
                            all_caches_same = False
                            break

                    if all_caches_same:
                        records_with_same_history += 1

                    obj_counter = Counter(intended_objects)
                    most_common_obj, count = obj_counter.most_common(1)[0] if intended_objects else (None, 0)
                    if selection['targetPointID'] != most_common_obj:
                        total_VOTE_eror_count += 1

                    if not selection['isCorrect']:
                        total_error_count += 1
                        if tech == "ControllerIntenSelect" or tech == "ControllerTracking":
                            intention_index = len(selection['historyCaches']) - 1
                            while intention_index >= 0:
                                if selection['historyCaches'][intention_index].get('confirmationValue', 0.0) == 0:
                                    break
                                intention_index -= 1
                            if intention_index >= 0:
                                intention_obj = selection['historyCaches'][intention_index]['intendedObjectID']
                                target_obj = selection['targetPointID']
                                if (intention_obj is not None and 
                                target_obj is not None and 
                                intention_obj == target_obj):
                                    heisenberg_error_count += 1
                        elif tech == "BareHandIntenSelect" or tech == "BareHandTracking":
                            history_caches = selection['historyCaches']
                            if len(selection['historyCaches']) == 0:
                                continue
                            middle_index = len(history_caches) // 2

                            velocityRots = [cache.get('velocityRot', 0) for cache in selection['historyCaches']]
                            start_index = max(0, len(velocityRots) - 14)
                            candidate_indices = [i for i in range(start_index, len(velocityRots)) if velocityRots[i] > 0.3]
                            peak_index = min(candidate_indices) if candidate_indices else middle_index
                            stable_index = peak_index
                            
                            while stable_index >= 0:
                                if velocityRots[stable_index] <= 0.001 and selection['historyCaches'][stable_index]['intendedObjectID'] != "null":
                                    break
                                stable_index -= 1
                            if stable_index >= 0:
                                stable_obj = selection['historyCaches'][stable_index]['intendedObjectID']
                                heisenberg_frame = selection['historyCaches'][stable_index]
                                target_obj = selection['targetPointID']
                                if (stable_obj == target_obj and not selection['isCorrect']):
                                    heisenberg_error_count += 1    
                            else:
                                intended_id = history_caches[middle_index]['intendedObjectID']
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

                                if intended_id == selection['targetPointID'] and not selection['isCorrect']: 
                                    heisenberg_error_count += 1
                        
                        # elif tech == "BareHandIntenSelect" or tech == "BareHandTracking":
                        #     velocityDIs = [cache.get('velocityDI', 0) for cache in selection['historyCaches']]
                        #     peak_index = velocityDIs.index(max(velocityDIs))
                        #     stable_index = peak_index
                        #     while stable_index >= 0 and velocityDIs[stable_index] >= 0.1:
                        #         stable_index -= 1
                        #     if stable_index >= 0:
                        #         stable_obj = selection['historyCaches'][stable_index]['intendedObjectID']
                        #         target_obj = selection['targetPointID']
                        #         if (stable_obj == target_obj):
                        #             stats['heisenberg_error'] += 1

    print(f"{'='*60}")
    print(f"{'技术统计结果':^60}")
    print(f"{'='*60}")
    print(f"{'技术名称:':<15} {tech_name}")
    print(f"{'='*60}")
    
    # 第一行：索引名
    print(f"{'总点击':<5} | {'有目标记录':<7} | {'无转移选择':<6} | {'总错误数':<7} | {'海森堡错误':<7} | {'VOTE错误数':<5} ")
    
    # 第二行：数值
    print(f"{click_count:<8} | {records_with_target:<1}({records_with_target/click_count:.2%}) | {records_with_same_history}({records_with_same_history/click_count:.2%}) | {total_error_count} ({total_error_count/click_count:.2%}) | {heisenberg_error_count} ({heisenberg_error_count/click_count:.2%}) | {total_VOTE_eror_count} ({total_VOTE_eror_count/click_count:.2%})")
    print(f"{'='*60}")
    
if __name__ == '__main__':
    main()

