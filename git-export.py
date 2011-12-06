#!/usr/bin/env python
import sys, optparse, StringIO, os, shutil, time
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

def getLatestRev(workDir):
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
        return False
    workDir = path.join(workDir, relDir)
    return path.abspath(workDir)

def export(workDir, outputDir, diff, last, verbose=False):
    """Copy files from repository to output dir."""
    # Abs paths
    workDir   = path.abspath(workDir)
    outputDir = path.abspath(outputDir)

    #print workDir, outputDir, diff, last
    if not path.exists(workDir):
        print "Repsitory dir not exists."
        return 2

    if  not path.exists(outputDir):
        os.makedirs(outputDir)

    workDir = getRepoRoot(workDir)
    if not workDir:
        # git will print the error message, something like "fatal: Not a git repository (or any of the parent directories): .git"
        return 2

    if last:
        cmd = "git log --pretty=format:%%h -n1 --skip=%s" % last
        p = Popen(cmd, shell=True, stdout=PIPE, cwd=workDir)
        rev = p.stdout.read()
        if len(rev) == 0:
            rev = ""
        diff = rev + ".." + getLatestRev(workDir)

    if diff:
        cmd = "git diff --name-status %s" % diff
        if verbose:
            print cmd
        p = Popen(cmd, shell=True, stdout=PIPE, cwd=workDir)
        logs = p.stdout.read()

    logs = StringIO.StringIO(logs)
    while True:
        line = logs.readline()
        if not line:
            break;
        parseLog(line.strip(), workDir, outputDir, verbose)
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
        workDir = os.getcwd()
    else:
        workDir = arguments[0]

        if workDir == 'help':
            p.print_help()
            sys.exit()

    if argLen <= 1:
        outputDir = '/tmp/%s_%d' % (os.path.basename(workDir), int(time.time()))
    else:
        outputDir = arguments[1]

    if not options.diff and not options.last:
        options.last = 1

    result = export(workDir, outputDir, 
                    options.diff, options.last, 
                    options.verbose)
    if result == 0:
        print 'Repsitory has been exported to %s' % outputDir
    sys.exit(result)

if __name__ == '__main__':
    main()
