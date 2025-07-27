from calendar import c
import numpy as np
import argparse
import json

from data_preprocess import load_json_data, save_data_to_json
def read_from_numpy(file_path):
    data = np.load(file_path, allow_pickle=True)
    return data.item()
    
def extract_all_wanted_data(data):
    all_selection_times = []
    all_correct_selection_times = []
    all_selection_errors = []
    all_H_selection_errors = []
    all_H_Offset_x = []
    all_H_Offset_y = []
    all_H_Offset_magnitude = []

    for data_item in data:
        correct_selection_times = [entry["clickDuration"] for entry in data_item["selectionSequence"] if float(entry["isCorrect"]) > 0]
        selection_times = [entry["clickDuration"] for entry in data_item["selectionSequence"]]
        selection_errors = [float(entry["isCorrect"]) for entry in data_item["selectionSequence"]]
        H_selection_errors = [float(1) if entry["HeisenbergError"] == 1 and entry["isCorrect"] == 0 else float(0) for entry in data_item["selectionSequence"]]

        for entry in data_item["selectionSequence"]:
            if "HeisenbergOffset" in entry and isinstance(entry["HeisenbergOffset"], list):
                h_offset = entry["HeisenbergOffset"]
                all_H_Offset_x.append(float(h_offset[0]))
                all_H_Offset_y.append(float(h_offset[1]))
                all_H_Offset_magnitude.append(np.sqrt(float(h_offset[0])**2 + float(h_offset[1])**2))
                # all_H_Offset_magnitude.append(h_offset)

        all_selection_times.extend(selection_times)
        all_selection_errors.extend(selection_errors)
        all_H_selection_errors.extend(H_selection_errors)
        all_correct_selection_times.extend(correct_selection_times)


    all_selection_times = np.array(all_selection_times)
    all_selection_errors = np.array(all_selection_errors)
    all_H_selection_errors = np.array(all_H_selection_errors)
    all_H_Offset_x = np.array(all_H_Offset_x)
    all_H_Offset_y = np.array(all_H_Offset_y)
    all_H_Offset_magnitude = np.array(all_H_Offset_magnitude)

    if len(all_selection_times) > 0:
        original_count = len(all_selection_times)

        mean = np.mean(all_selection_times)
        std = np.std(all_selection_times)
        lower_bound = mean - 3 * std
        upper_bound = mean + 3 * std
        print(f"lower_bound: {lower_bound}")
        mask = (all_selection_times >= 0.1) & (all_selection_times <= upper_bound)

        all_selection_times = all_selection_times[mask]
        all_selection_errors = all_selection_errors[mask]
        all_H_selection_errors = all_H_selection_errors[mask]
        all_H_Offset_x = all_H_Offset_x[mask]
        all_H_Offset_y = all_H_Offset_y[mask]
        all_H_Offset_magnitude = all_H_Offset_magnitude[mask]

        filtered_count = original_count - len(all_selection_times)
        print(f"过滤掉的数据点数量: {filtered_count}")
        print(f"过滤前: {original_count} 个, 过滤后: {len(all_selection_times)} 个")

    all_correct_selection_times = all_selection_times[all_selection_errors > 0].tolist()

    return len(all_correct_selection_times), all_selection_times, all_selection_errors, all_H_selection_errors, all_H_Offset_x, all_H_Offset_y, all_H_Offset_magnitude


def get_global_avg_and_std(selection_times):
    # print("sum: ", np.sum(selection_times))
    # print("len: ", len(selection_times))

    # selection_times = np.array(selection_times)

    # original_mean = np.mean(selection_times)
    # original_std = np.std(selection_times)

    # lower_bound = original_mean - 3 * original_std
    # upper_bound = original_mean + 3 * original_std

    # filtered_times = selection_times[(selection_times >= lower_bound) & (selection_times <= upper_bound)]
    # print(f"数据过滤: 原始{len(selection_times)}个, 过滤后{len(filtered_times)}个, 删除{len(selection_times)-len(filtered_times)}个异常值")
    # avg = np.mean(filtered_times)
    # std_dev = np.std(filtered_times)
    # sem = std_dev / np.sqrt(len(filtered_times)) if len(filtered_times) > 0 else 0
    # print("average: ", np.mean(selection_times))
    # print("过滤后的平均值: ", avg)
    # print("过滤后的标准差: ", std_dev)
    # print("过滤后的标准误: ", sem)
    # return avg, std_dev, sem
    avg = np.mean(selection_times)

    std_dev = np.std(selection_times)
    print("std_dev: ", std_dev)
    
    sem = std_dev / np.sqrt(len(selection_times))
    print("sem: ", sem)
    return avg, std_dev, sem

def compute_global_error_rate(selection_errors):
    accuracy_rate = np.mean(selection_errors)
    print("accuracy: ", accuracy_rate)
    accuracy_sem = np.std(selection_errors) / np.sqrt(len(selection_errors))
    print("accuracy_sem: ", accuracy_sem)
    print("error rate: ", 1-accuracy_rate)
    return accuracy_rate, accuracy_sem

def compute_global_H_error_rate(H_selection_errors):
    H_error_rate = np.mean(H_selection_errors)
    print("H_error_rate: ", H_error_rate)
    H_error_rate_sem = np.std(H_selection_errors) / np.sqrt(len(H_selection_errors))
    print("H_error_rate_sem: ", H_error_rate_sem)
    print("")
    return H_error_rate, H_error_rate_sem

def compute_global_HeisenbergOffset(heisenberg_offset):
    global_HeisenbergOffset = np.mean(heisenberg_offset)
    print("global_HeisenbergOffset: ", global_HeisenbergOffset)
    global_HeisenbergOffset_sem = np.std(heisenberg_offset) / np.sqrt(len(heisenberg_offset))
    print("global_HeisenbergOffset_sem: ", global_HeisenbergOffset_sem)
    print("")
    return global_HeisenbergOffset, global_HeisenbergOffset_sem

def compute_HeisenbergOffset_direction(all_H_Offset_x, all_H_Offset_y):
    count_right_top = 0
    count_right_down = 0
    count_left_top = 0
    count_left_down = 0
    count_in_axis = 0

    for x, y in zip(all_H_Offset_x, all_H_Offset_y):
            if x > 0 and y > 0:
                count_right_top += 1
            elif x > 0 and y < 0:
                count_right_down += 1
            elif x < 0 and y > 0:
                count_left_top += 1
            elif x < 0 and y < 0:
                count_left_down += 1
            else:
                count_in_axis += 1

    print(f"count_right_top: {count_right_top}")
    print(f"count_right_down: {count_right_down}")
    print(f"count_left_top: {count_left_top}")
    print(f"count_left_down: {count_left_down}")
    print(f"count_in_axis: {count_in_axis}")

    return count_right_top, count_right_down, count_left_top, count_left_down, count_in_axis

def save_to_numpy(data, file_path):
    np.save(file_path, data) 

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

    radius_range = ['radius_007', 'radius_014', 'radius_021']
    spacing_range = ['spacing_03', 'spacing_05', 'spacing_07']

    def analyze_data(partial_name):
        data_file_path = './output_json/' + full_name + "_" + partial_name + "_data.json"
        data = load_json_data(data_file_path)

        print(f'tech: {full_name}, partial_name: {partial_name}')


        if data is None:
            print("The data is None for ", full_name, " and ", partial_name)

        click_count, all_selection_times, all_selection_errors, H_selection_errors, all_H_Offset_x, all_H_Offset_y, all_H_Offset_magnitude = extract_all_wanted_data(data)
        global_avg_selection_time, global_std_selection_time, global_sem_selection_time = get_global_avg_and_std(all_selection_times)

        global_error_rate, global_error_rate_sem = compute_global_error_rate(all_selection_errors)

        global_H_error_rate, global_H_error_rate_sem = compute_global_H_error_rate(H_selection_errors)

        global_H_Offset_magnitude, global_H_Offset_sem = compute_global_HeisenbergOffset(all_H_Offset_magnitude)

        count_right_top, count_right_down, count_left_top, count_left_down, count_in_axis = compute_HeisenbergOffset_direction(all_H_Offset_x, all_H_Offset_y)

        processed_data = {
            "technique": full_name,
            "global_avg_selection_time": global_avg_selection_time,
            "global_std_selection_time": global_std_selection_time,
            "global_sem_selection_time": global_sem_selection_time,
            "global_error_rate": global_error_rate,
            "global_error_rate_sem": global_error_rate_sem,
            "global_H_error_rate": global_H_error_rate,
            "global_H_error_rate_sem": global_H_error_rate_sem,
            "global_H_offset_magnitude": global_H_Offset_magnitude,
            "global_H_offset_sem": global_H_Offset_sem,
            "count_right_top": count_right_top,
            "count_right_down": count_right_down,
            "count_left_top": count_left_top,
            "count_left_down": count_left_down,
            "count_in_axis": count_in_axis
        }
        save_to_numpy(processed_data, './output_numpy/' + full_name + "_" + partial_name + "_data.npy")

    for r in radius_range:
        analyze_data(r)

    for s in spacing_range:
        analyze_data(s)

if __name__ == '__main__':
    main()