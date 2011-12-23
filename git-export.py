#!/usr/bin/env python
import sys, optparse, StringIO, os, shutil, time
from os import path
from subprocess import Popen, PIPE, call

def parseLog(log, repoRoot, outputDir, verbose=False):
    """Parsing every single log printed from git log command"""
    if log.startswith('D'):
        print log
        return False
    else:
        if verbose:
            print log
    return log.split("\t")[1]

def dumpFile(innerFilePath, repoRoot, outputDir):
    """Dump file from the given path which is sub path relative to the repository root."""
    dirName = os.path.dirname(innerFilePath)
    if dirName != innerFilePath:
        destPath = os.path.join(outputDir, dirName)
        if not os.path.exists(destPath):
            os.makedirs(destPath)

    #print os.path.join(repoRoot, innerFilePath), os.path.join(outputDir, innerFilePath)
    shutil.copy2(os.path.join(repoRoot, innerFilePath), os.path.join(outputDir, innerFilePath))

def getLatestRevHash(repoRoot):
    """Get the latest revision hash code"""
    cmd = "git log --pretty=format:%h -n1"
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=repoRoot)
    rev = p.stdout.read()
    if len(rev) == 0:
        return ""
    else:
        return rev

def getRepoRoot(sourceDir):
    """Return the abs path to the root repository dir"""
    # If the work dir is not the root of the repository dir, then get the
    # the relative path to the root.(../../)
    cmd = "git rev-parse --show-cdup"
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=sourceDir)
    relDir = p.stdout.readlines()
    if len(relDir) > 0:
        relDir = relDir[0].strip()
    else:
        return False
    sourceDir = path.join(sourceDir, relDir)
    return path.abspath(sourceDir)

def export(sourceDir, outputDir, diff, last, verbose=False):
    """Copy files from repository to output dir."""
    # Abs paths
    sourceDir   = path.abspath(sourceDir)
    outputDir = path.abspath(outputDir)

    #print sourceDir, outputDir, diff, last
    if not path.exists(sourceDir):
        print "Repsitory dir not exists."
        return 2

    if  not path.exists(outputDir):
        os.makedirs(outputDir)

    repoRoot = getRepoRoot(sourceDir)
    if not repoRoot:
        # git will print the error message, something like "fatal: Not a git repository (or any of the parent directories): .git"
        return 2

    if last:
        cmd = "git log --pretty=format:%%h -n1 --skip=%s" % last
        p = Popen(cmd, shell=True, stdout=PIPE, cwd=repoRoot)
        rev = p.stdout.read()
        if len(rev) == 0:
            rev = ""
        diff = rev + ".." + getLatestRevHash(repoRoot)

    if diff:
        cmd = "git diff --name-status %s" % diff
        if verbose:
            print cmd
        p = Popen(cmd, shell=True, stdout=PIPE, cwd=repoRoot)
        logs = p.stdout.read()

    logs = StringIO.StringIO(logs)
    while True:
        line = logs.readline()
        if not line:
            break;
        innerFilePath = parseLog(line.strip(), repoRoot, outputDir, verbose)
        if innerFilePath:
            dumpFile(innerFilePath, repoRoot, outputDir)
    return 0

def main():
    """Main Function"""
    p = optparse.OptionParser(description="Export files from git repository", 
                                prog=os.path.basename(sys.argv[0]), 
                                version="0.1a", 
                                usage="%prog [WORK_DIR] [OUTPUT_DIR] -v --diff=[hash..hash] -l [number]")
    p.add_option("--diff", "-d", action="store", dest="diff")
    p.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False)
    p.add_option("--last", "-l", action="store", dest="last")

    options, arguments = p.parse_args()
    argLen = len(arguments)

    if argLen == 0:
        sourceDir = os.getcwd()
    else:
        sourceDir = arguments[0]

        if sourceDir == 'help':
            p.print_help()
            sys.exit()

    if argLen <= 1:
        outputDir = '/tmp/%s_%d' % (os.path.basename(sourceDir), int(time.time()))
    else:
        outputDir = arguments[1]

    if not options.diff and not options.last:
        options.last = 1

    result = export(sourceDir, outputDir, 
                    options.diff, options.last, 
                    options.verbose)
    if result == 0:
        print 'Repsitory has been exported to %s' % outputDir
        osname = os.uname()[0]
        if osname == 'Linux': # Linux gui
            try:
                call(['xdg-open', outputDir])
            except Exception, e:
                pass
        elif osname == 'Darwin': # Mac osx
            try:
                call(['open', outputDir])
            except Exception, e:
                pass
            
    sys.exit(result)

if __name__ == '__main__':
    main()
