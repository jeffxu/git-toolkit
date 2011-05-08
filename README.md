# Example

This example will export last 4 commits from /home/develop/workspace/test to /tmp/test
    git-export.py /home/develop/workspace/test /tmp/test -l4

Blow command will export commits between a4401fb768 to c904d331f from subdirectory workspace/project to parent tmp directory.
    git-export.py workspace/project ../tmp -d c904d331f..a4401fb768

**Bash version of the git-export is deprecated.**

Blow command will export commits between a4401fb768 to c904d331f of subdirectory workspace/project to parent directory tmp.
    git-export -w workspace/project -o ../tmp -v -d c904d331f..a4401fb768

Blow command will export all modified files which have not been committed to tmp directory.
    git-export -w workspace/project -o ../tmp -v
