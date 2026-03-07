import os
import re
import argparse
import logging

logging.basicConfig(
    filename="rename_log.txt",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class FileScanner:
    def __init__(self, folder_path, recursive=False):
        self.folder_path = folder_path
        self.recursive = recursive

    def get_files(self):
        files = []
        if self.recursive:
            for root, dirs, filenames in os.walk(self.folder_path):
                for f in filenames:
                    files.append(os.path.join(root, f))
        else:
            for f in os.listdir(self.folder_path):
                full_path = os.path.join(self.folder_path, f)
                if os.path.isfile(full_path):
                    files.append(full_path)
        files.sort()
        return files

class RenamePlan:
    def __init__(self, files, existing_files, base_name, prefix="", suffix=""):
        self.files = files
        self.existing_files = set(existing_files)
        self.base_name = base_name
        self.prefix = prefix
        self.suffix = suffix
        self.mapping = {}

    def generate(self):
        used_indices = set()
        pattern = re.compile(rf"{re.escape(self.base_name)}_(\d+)$")
        for fname in self.existing_files:
            match = pattern.match(os.path.splitext(os.path.basename(fname))[0])
            if match:
                used_indices.add(int(match.group(1)))

        counter = 1
        for old in self.files:
            while counter in used_indices:
                counter += 1
            ext = os.path.splitext(old)[1]
            new_name = f"{self.prefix}{self.base_name}_{counter}{self.suffix}{ext}"
            new_path = os.path.join(os.path.dirname(old), new_name)
            self.mapping[old] = new_path
            used_indices.add(counter)
            counter += 1

    def preview(self):
        return [(old,new) for old, new in self.mapping.items()]

class RenamerEngine:
    def __init__(self, rename_plan: RenamePlan):
        self.rename_plan = rename_plan
        self.success = []
        self.failed = []

    def execute(self):
        for old, new in self.rename_plan.mapping.items():
            try:
                os.rename(old, new)
                self.success.append((old, new))
                logging.info(f"Renamed {old} -> {new}")
            except Exception as e:
                self.failed.append((old, str(e)))
                logging.error(f"Failed to rename {old} -> {new}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Smart Batch Renamer")
    parser.add_argument("folder", help="Folder path to rename files in")
    parser.add_argument("base", help="New base name")
    parser.add_argument("--prefix", default="", help="Prefix to add")
    parser.add_argument("--suffix", default="", help="Suffix to add")
    parser.add_argument("--recursive", action="store_true", help="Rename files recursively")
    parser.add_argument("--dry-run", action="store_true", help="Preview rename without applying")
    args = parser.parse_args()

    scanner = FileScanner(args.folder, recursive=args.recursive)
    files = scanner.get_files()
    existing_files = files.copy()
    rename_plan = RenamePlan(files, existing_files, args.base, prefix=args.prefix, suffix=args.suffix)
    rename_plan.generate()

    if args.dry_run:
        print("Dry-run preview: ")
        for old, new in rename_plan.preview():
            print(f"{old} -> {new}")
        confirm = input("Proceed with rename? (y/n): ")
        if confirm.lower() != "y":
            print("Rename cancelled.")
            logging.info("Dry-run cancelled by user")
            return

    engine = RenamerEngine(rename_plan)
    engine.execute()

    print("Rename complete.")
    logging.info("Rename complete.")
    if engine.failed:
        print("Failed renames:")
        for old, err in engine.failed:
            print(f"{old}: {err}")
            logging.warning(f"Failed rename: {old} -> {err}")

if __name__ == "__main__":
    main()