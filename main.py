import os
import re
import argparse

class FileScanner:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def get_files(self):
        """Return a sorted list of files (ignore directories)"""
        all_items = os.listdir(self.folder_path)
        files = [f for f in all_items if os.path.isfile(os.path.join(self.folder_path, f))]
        files.sort()
        return files

class RenamePlan:
    def __init__(self, files, existing_files, base_name):
        self.files = files
        self.existing_files = set(existing_files)
        self.base_name = base_name
        self.mapping = {}

    def generate(self):
        """Generate rename mapping with collision handling"""
        used_indices = set()

        pattern = re.compile(rf"{re.escape(self.base_name)}_(\d+)$")
        for fname in self.existing_files:
            match = pattern.match(os.path.splitext(fname)[0])
            if match:
                used_indices.add(int(match.group(1)))

        counter = 1
        for old in self.files:
            while counter in used_indices:
                counter += 1
            ext = os.path.splitext(old)[1]
            new_name = f"{self.base_name}_{counter}{ext}"
            self.mapping[old] = new_name
            used_indices.add(counter)
            counter += 1

    def preview(self):
        """Return a list of tuples for dry-run"""
        return [(old,new) for old, new in self.mapping.items()]

class RenamerEngine:
    def __init__(self, folder_path, rename_plan: RenamePlan):
        self.folder_path = folder_path
        self.plan = rename_plan
        self.success = []
        self.failed = []

    def execute(self):
        """Apply the rename mapping safely with exception handling"""
        for old, new in self.plan.mapping.items():
            old_path = os.path.join(self.folder_path, old)
            new_path = os.path.join(self.folder_path, new)
            try:
                os.rename(old_path, new_path)
                self.success.append((old, new))
            except Exception as e:
                self.failed.append((old, str(e)))

def main():
    parser = argparse.ArgumentParser(description="Smart Batch Renamer")
    parser.add_argument("folder", help="Folder path to rename files in")
    parser.add_argument("base", help="New base name")
    parser.add_argument("--dry-run", action="store_true", help="Preview rename without applying")
    args = parser.parse_args()

    scanner = FileScanner(args.folder)
    files = scanner.get_files()
    existing_files = files.copy()
    rename_plan = RenamePlan(files, existing_files, args.base)
    rename_plan.generate()

    if args.dry_run:
        print("Dry-run preview: ")
        for old, new in rename_plan.preview():
            print(f"{old} -> {new}")
        confirm = input("Proceed with rename? (y/n): ")
        if confirm.lower() != "y":
            print("Rename cancelled.")
            return

    engine = RenamerEngine(args.folder, rename_plan)
    engine.execute()

    print("Rename complete.")
    if engine.failed:
        print("Failed renames:")
        for old, err in engine.failed:
            print(f"{old}: {err}")

if __name__ == "__main__":
    main()