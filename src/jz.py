import geohash2
import pandas as pd

# 读取Excel文件
file_path = '苏州怪兽-1359112597-1754970439985.xlsx' # 修改为你的文件路径
df = pd.read_excel(file_path)


# 确保Geohash列存在
if 'geohash' not in df.columns:
    raise ValueError("Excel文件中没有找到'Geohash'这一列。")

# 转换Geohash列为经纬度
def geohash_to_latlong(geohash_str):
    try:
        lat, lon = geohash2.decode(geohash_str)# 使用geohash2库解码
        return lat, lon
    except Exception as e:
        return None, None # 如果Geohash解码失败，返回None

# 应用转换函数并生成新的列
df[['Latitude', 'Longitude']] = df['geohash'].apply(geohash_to_latlong).apply(pd.Series)

# 将处理后的DataFrame保存为新的Excel文件
output_file_path = '苏州怪兽-1359112597-1754970439985_converted_file_1.xlsx' # 输出文件名
df.to_excel(output_file_path, index=False)

print(f"经纬度转换完成，文件已保存为 {output_file_path}")