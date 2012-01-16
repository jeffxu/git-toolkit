# Summary
The main idea behind the git export and git ftp is to help developer reduce their time in maintaining web application during the rapidly iterate milestone release and bug fixed.

**warning** The revision of the exported or uploaded files are remain the latest revision.

# Help

## Git export

Export files in last 4 commits, copy from /home/develop/workspace/test to /tmp/test.

    gitexport.py /home/develop/workspace/test /tmp/test -l4

Export files between the commits a4401fb768 to c904d331f, copy from subdirectory workspace/project to parent tmp directory.

    gitexport.py workspace/project ../tmp -r c904d331f..a4401fb768

## Git ftp
The most of the usage are the same as what we do in git export, addtionally add 3 flags to tell the script what to do when conflict occured.

- --silence Ivisible all log info, .gitftp.cfg file must given and settings must set properly, or the script will be interrupted without messages. Force to overwrite and remove remote file. 
- --force  Force to overwrite and remove remote files.
- --increase  Only add files, ignore conflicts and remove.

If none of these flag applied, script will ask user for further action when conflicts occured.

Upload last 5 commits with force overwrite and remove.

    gitftp.py project -l5 --force

##*Bash version of the git-export will not be maintained.*

Export between the commits a4401fb768 to c904d331f, copy from subdirectory workspace/project to parent directory tmp.

    git-export -w workspace/project -o ../tmp -v -d c904d331f..a4401fb768

Export all modified files which have not been committed to tmp directory.

    git-export -w workspace/project -o ../tmp -v
