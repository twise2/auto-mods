#! /usr/bin/env python3
"""Writes local-mod-description.txt into a mod's info.json Description
field, leaving every other field (Author, CacheStatus, Title) untouched.
Kept as a separate step (not hand-edited in info.json directly) so the
description lives in the repo, gets updated alongside the code that
changes what it describes, and can't silently drift out of sync.
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('description_file', type=Path)
    parser.add_argument('info_json', type=Path)
    args = parser.parse_args()

    description = args.description_file.read_text(encoding='utf-8').strip()

    with args.info_json.open(encoding='utf-8') as f:
        info = json.load(f)
    info['Description'] = description

    with args.info_json.open('w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False)

    print(f'Updated Description in {args.info_json}')


if __name__ == '__main__':
    main()
