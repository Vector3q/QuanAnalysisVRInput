import os

def get_all_json_files(root_path):
    json_files = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files
