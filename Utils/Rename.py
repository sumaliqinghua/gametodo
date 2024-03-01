import os

# 指定需要重命名文件的目录
directory_path = '/Users/popgo/project/python/gametodo/Assets/mp3'

# 获取指定目录下所有的mp3文件
mp3_files = [f for f in os.listdir(directory_path) if f.endswith('.mp3')]

# 对文件进行排序，以确保重命名的顺序
mp3_files.sort()

# 重命名文件
for i, filename in enumerate(mp3_files, start=10):
    # 构建旧的文件路径和新的文件路径
    old_file = os.path.join(directory_path, filename)
    new_file = os.path.join(directory_path, f"{i}.mp3")
    # //X:如果里面已经有数字了，这次的记得改前缀，否则会覆盖
    # 重命名文件
    os.rename(old_file, new_file)
    print(f"Renamed '{filename}' to '{i}.mp3'")

print("Renaming complete.")