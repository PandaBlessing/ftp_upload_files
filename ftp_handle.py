#!/usr/bin/python
# coding:utf-8

import ftplib
import os
import loadConfig

__author__ = 'wfq'
__date__ = '2018-11-23'
__version = 1.0


class MyFtp():
    def __init__(self):
        config = loadConfig.load_json()
        setting = self.setting = config[config['start']]

        self.host = setting['host']
        self.user = setting['user']
        self.pwd = setting['pwd']
        # 上传文件夹到指定位置
        self.remote_path = setting['remote_path']
        self.local_path = setting['local_path']
        # 不需要上传的文件
        self.not_upload_list = setting['not_upload_list']

        # 建立ftp链接
        self.ftp = self._connect()

    def _connect(self):
        '''
        建立FTP链接
        '''
        print('Connecting to FTP:')
        ftp = ftplib.FTP(self.host)
        response = ftp.login(self.user, self.pwd)
        print(response)
        return ftp

    def upload_dir(self, local_dir, remote_dir):
        '''
        上传目录
        '''
        ftp = self.ftp
        try:
            ftp.mkd(remote_dir)
        except Exception as e:
            print(e)

        str_sep = os.sep
        # 去掉路径字符串最后的分隔符'/'，如果有的话
        if local_dir[-1] == str_sep:
            local_dir = local_dir[0:-1]

        for root, dirs, files in os.walk(local_dir):
            for filespath in files:
                local_file = os.path.join(root, filespath)
                a = local_file.replace(local_dir + str_sep, '')
                remote_file = os.path.join(remote_dir, a)
                if os.path.sep == '\\':
                    remote_file = remote_file.replace('\\', '/')
                try:
                    self.upload_file(local_file, remote_file)
                except Exception as e:
                    print(e)
            
            for name in dirs:
                local_path = os.path.join(root, name)
                a = local_path.replace(local_dir + str_sep, '')
                remote_path = os.path.join(remote_dir, a)
                if os.path.sep == '\\':
                    remote_path = remote_path.replace('\\', '/')
                try:
                    ftp.mkd(remote_path)
                    print('创建目录=== ', remote_path)
                except Exception as e:
                    print(e)
        print('上传完成！')

    def upload_file(self, local_path, remote_path):
        '''
            上传文件
        '''
        ftp = self.ftp
        base_name = os.path.basename(local_path)
        print('上传文件=== ', base_name)
        not_upload_list = self.not_upload_list
        if base_name in not_upload_list:
            print('忽略该文件=== ', local_path)
            return
        f = open(local_path, 'rb')
        ftp.storbinary('STOR ' + remote_path, f)
        print('上传完成，存储位置=== ', os.path.dirname(remote_path))

    def delete_ftp_files(self, path):
        '''
        删除远程服务器文件
        '''
        ftp = self.ftp
        print('开始删除该处文件==== ', path)

        def delete(p):
            files = ftp.nlst(p)
            if files is None or len(files) == 0:
                try:
                    ftp.rmd(p)
                    print('删除目录=== ', p)
                except Exception as e:
                    print('删除失败=== ', p)
                    print('不存在该目录=== ', e)
                    pass
            else:
                for file in files:
                    try:
                        # 尝试删除文件
                        ftp.delete(os.path.join(p, file))
                        print('删除文件=== ', file)
                    except Exception as e:
                        try:
                            # 尝试删除目录
                            ftp.rmd(os.path.join(p, file))
                            print('删除目录=== ', os.path.join(p, file))
                        except Exception as e:
                            # 目录不为空时，递归删除子目录
                            delete(os.path.join(p, file))
                # 尝试删除该目录所在的目录
                delete(p)
        delete(path)


if __name__ == "__main__":
    my_ftp = MyFtp()
    my_ftp.delete_ftp_files(my_ftp.remote_path)
    my_ftp.upload_dir(my_ftp.local_path, my_ftp.remote_path)
