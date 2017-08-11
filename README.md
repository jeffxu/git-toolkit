# Summary
The main idea behind the git export and git ftp is to help developer reduce their time in maintaining web application during the rapidly iterate milestone release and bug fixed.

**warning** The revision of the exported or uploaded files are remain the latest revision.

# Help

## Git export

Export files in last 4 commits, copy from /home/develop/workspace/test to /tmp/test.

    gitexport.py /home/develop/workspace/test /tmp/test -l4

Export files between the commits a4401fb768 to c904d331f, copy from subdirectory workspace/project to parent tmp directory.

    gitexport.py workspace/project ../tmp -r c904d331f..a4401fb768


## *Bash version of the git-export will not be maintained.*

Export between the commits a4401fb768 to c904d331f, copy from subdirectory workspace/project to parent directory tmp.

    git-export -w workspace/project -o ../tmp -v -d c904d331f..a4401fb768

Export all modified files which have not been committed to tmp directory.

    git-export -w workspace/project -o ../tmp -v
