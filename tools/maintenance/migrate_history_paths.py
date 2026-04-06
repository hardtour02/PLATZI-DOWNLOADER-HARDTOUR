import json
from pathlib import Path

downloads_file = Path("data/downloads.json")
if not downloads_file.exists():
    print("No downloads.json found")
    exit()

with open(downloads_file, "r", encoding="utf-8") as f:
    data = json.load(f)

courses = data.get("courses", {})
modified = False

for slug, info in courses.items():
    path = info.get("path")
    if path:
        # Convert absolute or relative 'Courses' path to 'data/courses'
        new_path = path.replace("\\Courses\\", "\\data\\courses\\")
        new_path = new_path.replace("/Courses/", "/data/courses/")
        if path.endswith("Courses") or "\\Courses" in path or "/Courses" in path:
             # Handle cases where it might be just 'Courses\Name'
             if not ("\\data\\courses\\" in new_path or "/data/courses/" in new_path):
                 new_path = path.replace("Courses", "data/courses")
        
        if new_path != path:
            print(f"Updating path for {slug}: {path} -> {new_path}")
            info["path"] = str(Path(new_path))
            modified = True
    
    # Update internal video links if any
    lessons_meta = info.get("lessons_metadata", {})
    for l_slug, l_info in lessons_meta.items():
        l_path = l_info.get("local_path")
        if l_path:
            new_l_path = l_path.replace("\\Courses\\", "\\data\\courses\\").replace("/Courses/", "/data/courses/")
            if new_l_path != l_path:
                l_info["local_path"] = str(Path(new_l_path))
                modified = True

if modified:
    with open(downloads_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("downloads.json updated successfully.")
else:
    print("No changes needed in downloads.json.")
