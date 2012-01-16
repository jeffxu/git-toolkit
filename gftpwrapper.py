#!/usr/bin/env python

from ftplib import FTP, error_perm, error_temp

class GftpWrapper(object):

    def __init__(self, host, account, password, port=21):
        """init ftp and login"""
        try:
            self.__ftp = FTP()
            self.__ftp.connect(host, port)
            self.__ftp.login(account, password)
            self.loginSuccess = True
        except error_perm:
            self.loginSuccess = False

    def mkdir(self, path):
        """Make dir recusivly"""
        prevPath = ''
        path = path.split('/')
        for p in path:
            if not prevPath:
                prevPath = p
            else:
                prevPath += '/' + p
            if not self.isPathExists(prevPath):
                try:
                    self.__ftp.mkd(prevPath)
                except error_temp:
                    return False

        return True

    def cd(self, path):
        """Change the current dir to the given path"""
        try:
            self.__ftp.cwd(path)
            return True
        except error_perm:
            return False

    def rm(self, path):
        """Rmoeve remote file."""
        try:
            self.__ftp.delete(path)
            return True
        except error_perm:
            return False

    def upload(self, localPath, remotePath):
        try:
            self.__ftp.storbinary('STOR ' + remotePath, open(localPath, 'rb'))
            return True
        except IOError:
            return False

    def isPathExists(self, path):
        """Check for given path whether exists."""
        try:
            self.__ftp.nlst(path)
            return True
        except error_temp:
            return False

    def close(self):
        self.__ftp.close()
