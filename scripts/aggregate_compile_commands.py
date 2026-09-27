#!/usr/bin/env python3
""" Merge the compile_commands.json of every daisyHat firmware test project
    into a single compile_commands.json at the repository root, so LSP tools
    (e.g. clangd) can see all CMake targets across the standalone projects.

    Each test project builds its own .build/ directory; CMake writes a
    compile_commands.json there during configure. This script collects them
    and merges the entries into one file.

    Usage:
        python3 scripts/aggregate_compile_commands.py [search_dir ...]

    Without arguments, the repository root (the parent of this script's
    directory) is searched recursively for .build/compile_commands.json files.
"""

import json
import os
import sys


def find_compile_commands(search_dirs):
    """ :return: sorted list of compile_commands.json paths found under the
                 given search directories (skipping .venv and .git trees) """
    found = []
    for base in search_dirs:
        base = os.path.abspath(base)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".venv", ".git")]
            if "compile_commands.json" in filenames:
                found.append(os.path.join(dirpath, "compile_commands.json"))
    return sorted(set(found))


def load_entries(path):
    """ :return: list of compile command entries from one compile_commands.json
                 file, with file paths resolved to absolute paths so the merged
                 file works regardless of where it is opened from """
    with open(path) as f:
        entries = json.load(f)
    # paths in the source file are relative to its directory
    origin = os.path.dirname(os.path.abspath(path))
    for entry in entries:
        directory = entry.get("directory") or origin
        if not os.path.isabs(directory):
            directory = os.path.normpath(os.path.join(origin, directory))
        entry["directory"] = directory
        source = entry.get("file")
        if source is not None and not os.path.isabs(source):
            entry["file"] = os.path.normpath(os.path.join(directory, source))
    return entries


def main(argv):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    search_dirs = argv or [repo_root]
    output = os.path.join(repo_root, "compile_commands.json")

    files = find_compile_commands(search_dirs)
    if not files:
        print("no .build/compile_commands.json files found; build the test "
              "projects first (e.g. 'daisyhat build examples')", file=sys.stderr)
        return 2

    merged = []
    for path in files:
        entries = load_entries(path)
        print("  {} ({} entries)".format(path, len(entries)))
        merged.extend(entries)

    with open(output, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print("wrote {} entries to {}".format(len(merged), output))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
