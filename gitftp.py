#!/usr/bin/env python
import optparse, os, sys, logging
from os import path

repoRoot = ''

logger = logging.getLogger('git-ftp')
formatter = logging.Formatter('%(asctime)s %(message)s')
hdlr = logging.StreamHandler()
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

def rm(remotePath, ftp, mod=1):
    ''' mod: 1 ask for futher action, remove or ignore.
             2 remove anyway.
             3 ignore
    '''
    global logger

    if mod == 1:
        reaction = raw_input('Delete the remote file: ' + remotePath + ' ? y/n')
        if reaction.lower() != 'y':
            return
    elif mod == 3:
        return

    logger.warning('Deleting... ' + remotePath)
    ftp.rm(remotePath)
    logger.warning('COMPLETE')

def upload(localPath, remotePath, ftp, conflic_mod=1):
    ''' conflic_mod: 1 ask user for futher action, overwrite or ignore.
                     2 overwrite.
                     3 ignore.
    '''
    global logger

    if ftp.isPathExists(remotePath):
        if conflic_mod == 1:
            reaction = raw_input('[Conflct]\nLocal: ' + localPath + 
                                 '\nRemote: ' + remotePath + 
                                 '\nw for overwrite, i for ignore: ')
            if reaction.lower() == 'w':
                conflic_mod = 2
            else:
                conflic_mod = 3
    else:
        # File not exists, continue to upload.
        conflic_mod = 2

    if conflic_mod == 2:
        idx = remotePath.rfind('/')
        if idx >= 0:
            parent = remotePath[0:idx]
            if not ftp.isPathExists(parent):
                ftp.mkdir(parent)

        #print localPath, remotePath
        logger.warning('UPLOADING... ' + localPath)
        ftp.upload(localPath, remotePath)
        logger.warning('COMPLETE')
    else:
        logger.warning('IGNORE ' + localPath)

def sync(localRelPath, remotePath, logs, ftp, mod=1):
    global repoRoot

    if ftp.cd(remotePath):
        for log in logs:
            # Filter the local path for futher target file upload or remote deletion.
            if localRelPath == '.' or log[1].startswith(localRelPath):
                if log[0] == 'D': # Delete remote file.
                    rm(log[1], ftp, mod)
                else: # upload file.
                    upload(repoRoot + log[1], log[1], ftp, mod)

def initSftpClient(config):
    transport = paramiko.Transport((config['host'], config['port']))
    transport.connect(config['user'], config['pwd'])
    sftp = paramiko.SFTPClient.from_transport(transport)

    return sftp

def readConfig(path, mode=False):
    import ConfigParser
    cfgPaser = ConfigParser.ConfigParser()
    cfgPaser.read(path)
    
    config = {}

    # If settings not defined, wait for the user to enter host name, user name and password.
    if not cfgPaser.has_option('setting', 'host'):
        if mode:
            return False
        else:
            config['host'] = raw_input('Please enter the ftp host: ')
    else:
        config['host'] = cfgPaser.get('setting', 'host', 0)

    if not cfgPaser.has_option('setting', 'user'): 
        if mode:
            return False
        else:
            config['user'] = raw_input('Please enter the ftp user name: ')
    else:
        config['user'] = cfgPaser.get('setting', 'user', 0)

    if not cfgPaser.has_option('setting', 'pwd'):
        if mode:
            return False
        else:
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
    global repoRoot, logger

    from gitexport import getRepoRoot, filelog
    p = optparse.OptionParser(description="Sync files to the ftp.", 
                                prog=os.path.basename(sys.argv[0]), 
                                version="0.1a", 
                                usage="%prog [WORK_DIR] -v -l [number]")
    p.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False)
    p.add_option("--last",    "-l", action="store", dest="last")
    #no log messages, .gitftp.cfg must given and settings must set properly, 
    # or app will be interrupted without messages.
    p.add_option("--silence", "-s", action="store_true", dest="silence_mode", default=False)
    #force overwrite and delete remote files.
    p.add_option("--force",   "-f", action="store_true", dest="force_mode", default=False)
    #increase only, ignore overwrite and delete.
    p.add_option("--increase",  "-i", action="store_true", dest="increase_mode", default=False)

    options, arguments = p.parse_args()
    argLen = len(arguments)

    if argLen == 0:
        sourceDir = os.getcwd()
    else:
        sourceDir = arguments[0]

    if not options.last:
        options.last = 1

    if options.silence_mode:
        logger.setLevel(logging.CRITICAL)
        mode = 2
    elif options.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    if options.force_mode:
        mode = 2
    elif options.increase_mode:
        mode = 3
    else:
        mode = 1

    repoRoot = getRepoRoot(sourceDir) + '/'
    logger.info('Repository root: ' + repoRoot)

    configPath = repoRoot + '.gitftp.cfg'
    config = readConfig(configPath, options.silence_mode)

    if not config:
        exit(2)

    if config['ftp_type'] == 'ftp':
        from gftpwrapper import GftpWrapper
        ftp = GftpWrapper(config['host'], config['user'], config['pwd'], config['port'])
    else:
        pass
        #ftp = initSftpClient(config)

    if not ftp.loginSuccess:
        exit(2)

    logs = filelog(repoRoot, options.last)
    sync(config['local'], config['remote'], logs, ftp, mode)

    ftp.close()

if __name__ == '__main__':
    main()
