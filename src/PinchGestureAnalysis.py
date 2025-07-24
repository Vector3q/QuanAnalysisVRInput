import json
import matplotlib.pyplot as plt

json_path = '..\data\Heisenberg\P1\Study1_ISO_Test_Varied_TargetSize\P1_ExperimentData_20250529_161221.json'

with open(json_path, 'r') as f:
    data = json.load(f)

print("\n-------    Experiment Data    -------\n")
print(f"Name: {data['username']}")
print(f"Age: {data['userAge']}")
print(f"Gender: {data['usergender']}")

distance_di_values = []

plt.figure(figsize=(8, 5), dpi=100)

for i, selection in enumerate(data['selectionSequence'], 1):
    print(f"\nselection {i}:")
    print(f"click duration: {selection['clickDuration']}s")
    print(f"is correct: {'是' if selection['isCorrect'] else '否'}")
    print(f"selected ID: {selection['selectedPointID']}")
    print(f"target ID: {selection['targetPointID']}")

    if 'historyCaches' in selection:
        print("\ndistanceDI Tendency:")
        di_values = []
        for idx, cache in enumerate(selection['historyCaches']):
            if 'distanceDI' in cache:
                di_values.append(cache['distanceDI'])
                print(f"timestamp: {idx}, distanceDI: {cache['distanceDI']}")
        
        if di_values:
            plt.plot(di_values, label=f'Pinch {i}')

plt.title('DI Velocity in Pinch Gesture', fontsize=14)
plt.xlabel('frame', fontsize=12)
plt.ylabel('DI Velocity', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True)
plt.show()