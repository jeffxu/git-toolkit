#!/usr/bin/env python
import sys, optparse, StringIO, os, shutil, time, logging
from os import path
from subprocess import Popen, PIPE, call

def dumpFile(innerFilePath, repoRoot, outputDir):
    """Dump file from the given path which is sub path relative to the repository root."""
    dirName = os.path.dirname(innerFilePath)
    if dirName != innerFilePath:
        destPath = os.path.join(outputDir, dirName)
        if not os.path.exists(destPath):
            os.makedirs(destPath)

    #print os.path.join(repoRoot, innerFilePath), os.path.join(outputDir, innerFilePath)
    shutil.copy2(os.path.join(repoRoot, innerFilePath), os.path.join(outputDir, innerFilePath))

def getLatestRevHash(sourceDir):
    """Get the latest revision hash code"""
    cmd = "git log --pretty=format:%h -n1"
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=sourceDir)
    rev = p.stdout.read()
    if len(rev) == 0:
        return ""
    else:
        return rev

def getRepoRoot(sourceDir):
    """Return the abs path to the root repository dir"""
    cmd = "git rev-parse --show-toplevel"
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=sourceDir)
    absPath = p.stdout.readlines()

    if len(absPath) > 0:
        absPath = absPath[0].strip()
    else:
        return False
    return absPath

def getRevisionByStep(lastStep, sourceDir):
    cmd = "git log --pretty=format:%%h -n1 --skip=%s" % lastStep
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=sourceDir)
    return p.stdout.read()

def filelog(repoRoot, diff):
    """ Generate the file logs """

    cmd = "git diff --name-status %s" % diff
    p = Popen(cmd, shell=True, stdout=PIPE, cwd=repoRoot)
    logs_raw = p.stdout.read()
    logs_raw = StringIO.StringIO(logs_raw)

    logs = []
    while True:
        line = logs_raw.readline()
        if not line:
            break;
        line = line.strip()
        logs.append(line.split('\t'))
        logging.info(line)

    return logs

def export(sourceDir, outputDir, diff):
    """Copy files from repository to output dir."""
    # Abs paths
    sourceDir = path.abspath(sourceDir)
    outputDir = path.abspath(outputDir)

    #print sourceDir, outputDir, last
    if not path.exists(sourceDir):
        logging.info("Repsitory dir not exists.")
        return 2

    if  not path.exists(outputDir):
        os.makedirs(outputDir)

    repoRoot = getRepoRoot(sourceDir)
    if not repoRoot:
        # git will print the error message, something like "fatal: Not a git repository (or any of the parent directories): .git"
        return 2

    logs = filelog(repoRoot, diff)
    for log in logs:
        if log[0] != 'D':
            dumpFile(log[1], repoRoot, outputDir)

    return 0

def main():
    """Main Function"""
    p = optparse.OptionParser(description="Export files from git repository", 
                                prog=os.path.basename(sys.argv[0]), 
                                version="0.2a", 
                                usage="%prog [WORK_DIR] [OUTPUT_DIR] -v -l [step] -r [revsion rev1..rev2]")
    p.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False)
    p.add_option("--last", "-l", action="store", dest="last")
    p.add_option("--rev", "-r", action="store", dest="revision")

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
        outputDir = '/tmp/gitexport_%s_%d' % (os.path.basename(sourceDir), int(time.time()))
    else:
        outputDir = arguments[1]

    if not options.last and not options.revision:
        options.last = 1

    if options.verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING

    logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)

    if options.revision:
        diff = options.revision
    elif options.last:
        rev = getRevisionByStep(options.last, sourceDir)
        if len(rev) == 0:
            rev = ""
        diff = rev + ".." + getLatestRevHash(sourceDir)


    result = export(sourceDir = sourceDir, outputDir = outputDir, 
                    diff = diff)
    if result == 0:
        logging.info('Repsitory has been exported to %s' % outputDir)
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
