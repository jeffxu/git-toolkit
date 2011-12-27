#!/usr/bin/env python
import optparse, os, sys
from os import path
from ftplib import FTP
import paramiko

def cd(path, ftp):
    if ftp.__class__ == FTP:
        try:
            ftp.cwd(path)
        except error_perm:
            print '### Could not change the remote working dir!'
            return False
    else:
        try:
            ftp.chdir(path)
        except IOError:
            print '### Could not change the remote working dir!'
            return False
    return True

def upload(localPath, remotePath, ftp):
    pass

def initSftpClient(config):
    transport = paramiko.Transport((config['host'], config['port']))
    transport.connect(config['user'], config['pwd'])
    sftp = paramiko.SFTPClient.from_transport(transport)

    return sftp

def initFtpClient(config):
    ftp = FTP()
    ftp.connect(config['host'], config['port'])
    ftp.login(config['user'], config['pwd'])

    return ftp

def readConfig(path, repoRoot):
    import ConfigParser
    cfgPaser = ConfigParser.ConfigParser()
    cfgPaser.read(path)
    
    config = {}

    # If settings not defined, wait for the user to enter host name, user name and password.
    if not cfgPaser.has_option('setting', 'host'):
        config['host'] = raw_input('Please enter the ftp host: ')
    else:
        config['host'] = cfgPaser.get('setting', 'host', 0)

    if not cfgPaser.has_option('setting', 'user'): 
        config['user'] = raw_input('Please enter the ftp user name: ')
    else:
        config['user'] = cfgPaser.get('setting', 'user', 0)

    if not cfgPaser.has_option('setting', 'pwd'):
        import getpass
        config['pwd'] = getpass.getpass('Please enter the password: ')
    else:
        config['pwd'] = cfgPaser.get('setting', 'pwd', 0)

    if not cfgPaser.has_option('setting', 'ftp_type'):
        config['ftp_type'] = 'ftp'
    else:
        config['ftp_type'] = cfgPaser.get('setting', 'ftp_type', 0)

    if not cfgPaser.has_option('setting', 'local_base_path'):
        config['local'] = repoRoot
    else:
        config['local'] = cfgPaser.get('setting', 'local_base_path', 0)

    if not cfgPaser.has_option('setting', 'remote_base_path'):
        config['remote'] = '.'
    else:
        config['remote'] = cfgPaser.get('setting', 'remote_base_path', 0)

    if not cfgPaser.has_option('setting', 'port'):
        if config['ftp_type'] == 'ftp':
            config['port'] = 21
        else:
            config['port'] = 22
    else:
        config['port'] = cfgPaser.get('setting', 'port', 0)
    return config

def main():
    from gitexport import getRepoRoot, filelog
    p = optparse.OptionParser(description="Sync files to the ftp.", 
                                prog=os.path.basename(sys.argv[0]), 
                                version="0.1a", 
                                usage="%prog [WORK_DIR] -v -l [number]")
    p.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False)
    p.add_option("--last", "-l", action="store", dest="last")

    options, arguments = p.parse_args()
    argLen = len(arguments)

    if argLen == 0:
        sourceDir = os.getcwd()
    else:
        sourceDir = arguments[0]

    repoRoot = getRepoRoot(sourceDir) + '/'
    configPath = repoRoot + '.gitftp.cfg'
    print repoRoot

    config = readConfig(configPath, repoRoot)
    print config

    if config['ftp_type'] == 'ftp':
        ftp = initFtpClient(config)
    else:
        ftp = initSftpClient(config)

    cd(config['remote'], ftp)

    ftp.close()
    # Below test file
    #sourceDir = path.abspath('.')
    #print filelog(getRepoRoot(sourceDir), 6)

if __name__ == '__main__':
    main()
