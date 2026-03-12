# Smart Batch Renamer

A Python CLI tool for safely renaming large batches of files with automatic numbering.

Supports prefix/suffix customization, recursive scanning, and dry-run preview to prevent accidental file changes.

## Features

* Batch rename multiple files with automatic numbering
* Prefix and suffix support
* Recursive folder scanning
* Dry-run mode to preview changes before applying
* Collision protection (skips files if target name already exists)
* Operation logging for safety and debugging

## Architecture

* **FileScanner** – collects files from a directory (optionally recursive)
* **RenamePlan** – generates a safe rename mapping
* **RenamerEngine** – executes the renaming process and handles errors
* **main()** – CLI interface and argument parsing

All operations are logged in `rename_log.txt`.

## Example Usage

Run from terminal:

Basic rename:

```
python main.py "C:\path\to\folder" file
```

Result:

```
a.txt → file_1.txt
b.txt → file_2.txt
c.txt → file_3.txt
```

Preview changes (recommended):

```
python main.py "C:\path\to\folder" file --dry-run
```

Add prefix:

```
python main.py "C:\path\to\folder" image --prefix holiday_
```

Add suffix:

```
python main.py "C:\path\to\folder" image --suffix _backup
```

Recursive rename:

```
python main.py "C:\path\to\folder" file --recursive
```

## Requirements

* Python 3.10+
* Standard library only (no external dependencies)

## Logging

All operations are logged to:

```
rename_log.txt
```

This includes:

* renamed files
* skipped files
* errors
* execution summary
