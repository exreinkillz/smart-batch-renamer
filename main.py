import os

folder_path = input("Enter folder path: ")
base_name = input("Enter new base name: ")

files = os.listdir(folder_path)

counter = 1

for file in files:
    old_path = os.path.join(folder_path, file)

    if not os.path.isfile(old_path):
        continue

    extension = os.path.splitext(file)[1]
    
    new_name = f"{base_name}_{counter}{extension}"
    new_path = os.path.join(folder_path, new_name)

    os.rename(old_path, new_path)
    counter += 1

print("Files renamed sucessfully")