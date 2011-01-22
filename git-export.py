#!/usr/bin/env python
import sys
import optparse
import StringIO
import os
import shutil
from os import path
from subprocess import Popen, PIPE

def parseLog(log, workDir, outputDir, verbose=False):
    """Parsing every single log printed from git log command"""
    if log.startswith('D'):
        print log
    else:
        if verbose:
            print log
        dumpFile(log.split("\t")[1], workDir, outputDir)

def dumpFile(path, workDir, outputDir):
    """Dump file from the path"""
    dir = os.path.dirname(path)
    if dir != path:
        destDir = os.path.join(outputDir, dir)
        if not os.path.exists(destDir):
            os.makedirs(destDir)

    #print os.path.join(workDir, path), os.path.join(outputDir, path)
    shutil.copy2(os.path.join(workDir, path), os.path.join(outputDir, path))

def read():
    """Reading last recorded hash value from .git-export file"""
    pass

def record(workDir):
    """Recording hash value to .git-export file. If not exits, create it."""
#   if not path.exists(path.join(workDir, '.git-export')):
#      None 

def getCurrentRev(workDir):
    """Get latest revision"""
    cmd = "git log --pretty=format:%h -n1"
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=workDir)
    rev = p.stdout.read()
    if len(rev) == 0:
        return ""
    else:
        return rev

def getRepoRoot(workDir):
    """Return the abs path to the root repository dir"""
    # If the work dir is not the root of the repository dir, then get the
    # the relative path to the root.(../../)
    cmd = "git rev-parse --show-cdup"
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=workDir)
    relDir = p.stdout.readlines()
    if len(relDir) > 0:
        relDir = relDir[0].strip()
    else:
        sys.exit(2)
    workDir = path.join(workDir, relDir)
    return path.abspath(workDir)

def export(workDir, outputDir, diff, last, record=False, read=False):
    """Copy files from repository to output dir."""
    # Abs paths
    workDir   = path.abspath(workDir)
    outputDir = path.abspath(outputDir)

    print workDir, outputDir, diff, last, record, read
    if not path.exists(workDir) or not path.exists(outputDir):
        print "Repsitory or output dir not exists."
        return 2

    workDir = getRepoRoot(workDir)

    if last:
        cmd = "git log --pretty=format:%%h -n1 --skip=%s" % last
        p = Popen(cmd, shell=True, stdout=PIPE, cwd=workDir)
        rev = p.stdout.read()
        if len(rev) == 0:
            rev = ""
        diff = rev + ".." + getCurrentRev(workDir)

    if diff:
        cmd = "git diff --name-status %s" % diff
        print cmd
        p = Popen(cmd, shell=True, stdout=PIPE, cwd=workDir)
        logs = p.stdout.read()

    #if read or record:
    logs = StringIO.StringIO(logs)
    while True:
        line = logs.readline()
        if not line:
            break;
        parseLog(line.strip(), workDir, outputDir)
    return 0

def main():
    """Main Function"""
    p = optparse.OptionParser(description="Export files from git repository", 
                                prog="argTest", 
                                version="0.1a", 
                                usage="%prog [WORK_DIR] [OUTPUT_DIR] -r -R --diff=[hash..hash] -l [number]")
    p.add_option("--diff", "-d", action="store", dest="diff")
    p.add_option("--record", "-R", action="store_true", dest="record", default=False)
    p.add_option("--read", "-r", action="store_true", dest="read", default=False)
    p.add_option("--last", "-l", action="store", dest="last")

    options, arguments = p.parse_args()
    argLen = len(arguments)
    if argLen >= 1:
        workDir = arguments[0]
        outputDir = "."
        if argLen > 1:
            outputDir = arguments[1]

        sys.exit(export(workDir, outputDir, 
                        options.diff, options.last, 
                        options.record, options.read))
    else:
        p.print_help()

if __name__ == '__main__':
    main()
