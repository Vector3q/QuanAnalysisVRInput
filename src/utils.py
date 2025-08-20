import os

# fp_train = list(range(1,19))
# fp_test = list(range(20,25))

fp_indi = [10]

fp_train = [1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,19,20,22,24]
fp_test = [3,8,18,21,23]
# fp_test = list(range(17, 18))

# 3 8 10 15 16 18 20 21 23 

def get_all_json_files(root_path):
    json_files = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files
