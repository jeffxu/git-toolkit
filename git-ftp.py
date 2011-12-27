#!/usr/bin/env python
from os import path
from git_export import getRepoRoot, filelog

def main():
    sourceDir = path.abspath('.')
    print filelog(getRepoRoot(sourceDir), 3)

if __name__ == '__main__':
    main()
