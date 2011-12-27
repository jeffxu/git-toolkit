#!/usr/bin/env python
import optparse, os, sys
from os import path
from ftplib import FTP, error_perm, error_temp
import paramiko

def mkdir(path, ftp):
    prevPath = ''
    path = path.split('/')
    path = path[:-1]
    for p in path:
        if not prevPath:
            prevPath = p
        else:
            prevPath += '/' + p
        try:
            ftp.nlst(prevPath)
        except error_temp:
            ftp.mkd(prevPath)

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

def rm(remotePath, ftp, mod=1):
    ''' mod: 1 ask for futher action, remove or ignore.
             2 remove anyway.
    '''
    if mod == 1:
        reaction = raw_input('Delete the remote file: ' + remotePath + ' ? y/n')
        if reaction == 'y':
            mod = 2
        else:
            return
    print remotePath

def upload(localPath, remotePath, ftp, conflic_mod=3):
    ''' conflic_mod: 1 overwrite.
                     2 ignore.
                     3 ask user for futher action, overwrite or ignore.
    '''
    if ftp.__class__ == FTP:
        try:
            ftp.nlst(remotePath)
            if conflic_mod == 3:
                reaction = raw_input('Local file ' + localPath + 
                                     ' confliced with the remote file' + remotePath + 
                                     ' , o for overwrite, i for ignore')
                if reaction == 'o':
                    conflic_mod = 1
                else:
                    conflic_mod = 2
        except error_temp:
            # File not exists, continue to upload.
            conflic_mod = 1
        if conflic_mod == 1:
            parent = remotePath[0:remotePath.rfind('/')]
            try:
                ftp.nlst(parent)
                ftp.storbinary('STOR ' + remotePath, open(localPath, 'rb'))
            except error_temp:
                mkdir(remotePath, ftp)
                ftp.storbinary('STOR ' + remotePath, open(localPath, 'rb'))
    else:
        # sftp
        pass

def initSftpClient(config):
    transport = paramiko.Transport((config['host'], config['port']))
    transport.connect(config['user'], config['pwd'])
    sftp = paramiko.SFTPClient.from_transport(transport)

    return sftp

def initFtpClient(config):
    try:
        ftp = FTP()
        ftp.connect(config['host'], config['port'])
        ftp.login(config['user'], config['pwd'])
    except error_perm:
        print '### Login failed!'
        return False

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

    if not options.last:
        options.last = 1

    repoRoot = getRepoRoot(sourceDir) + '/'
    configPath = repoRoot + '.gitftp.cfg'

    config = readConfig(configPath, repoRoot)
    #print config

    if config['ftp_type'] == 'ftp':
        ftp = initFtpClient(config)
    else:
        ftp = initSftpClient(config)

    if not ftp:
        exit(2)

    if cd(config['remote'], ftp):
        logs = filelog(repoRoot, options.last)
        for log in logs:
            # Filter the local path for futher target file upload or remote deletion.
            if config['local'] == '.' or log[1].startswith(config['local']):
                if log[0] == 'D': # Delete remote file.
                    rm(log[1], ftp)
                else: # upload file.
                    upload(repoRoot + log[1], log[1], ftp)

    ftp.close()
    # Below test file
    #sourceDir = path.abspath('.')

if __name__ == '__main__':
    main()
