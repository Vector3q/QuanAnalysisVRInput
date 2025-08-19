import os

fp_train = list(range(1, 8)) + list(range(9,18)) 
fp_test = list(range(8, 9)) + list(range(18,24))

# fp_train = list(range(1, 18)) 
# fp_test = list(range(18,24))

def get_all_json_files(root_path):
    json_files = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files
