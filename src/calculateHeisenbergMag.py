import pandas as pd
import numpy as np

def calculate_controller_tracking_mean_angle(csv_file_path):

    try:
        df = pd.read_csv(csv_file_path)
        
        controller_tracking_data = df[df['technique'] == 'ControllerIntenSelect']
        
        if controller_tracking_data.empty:
            print("can not find the data about ControllerTracking")
            return None
            
        mean_angle = controller_tracking_data['heisenberg_angle'].mean()
        
        print(f"ControllerTracking data point: {len(controller_tracking_data)}")
        print(f"heisenberg_angle mean: {mean_angle:.6f}")
        print(f"heisenberg_angle std: {controller_tracking_data['heisenberg_angle'].std():.6f}")
        print(f"heisenberg_angle min: {controller_tracking_data['heisenberg_angle'].min():.6f}")
        print(f"heisenberg_angle max: {controller_tracking_data['heisenberg_angle'].max():.6f}")
        
        return mean_angle
        
    except FileNotFoundError:
        print(f"can not find the file: {csv_file_path}")
        return None
    except Exception as e:
        print(f"error when process the file: {e}")
        return None

if __name__ == "__main__":
    csv_file = "c:\\Research\\3DUI\\Heisenberg\\QuanAnalysisVRInput\\src\\output_csv\\csv_files.csv"
    
    result = calculate_controller_tracking_mean_angle(csv_file)
    
    if result is not None:
        print(f"\nresult: {result:.6f}")