# 主程序部分
# By Bing_Yanchi
from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from hashlib import md5
import threading,sys,yaml,os,time,json

# 检查用户文件 md5 值
def check_file_md5(self):
    file_name = public_data['user_config']
    with open(file_name, 'rb') as fp:
        data = fp.read()
    return md5(data).hexdigest()

class DummyMD5Authorizer(DummyAuthorizer):
    def validate_authentication(self, username, password):
        if sys.version_info >= (3, 0):
            password = password.encode('latin1')
        hash = md5(password).hexdigest()
        try:
            if self.user_table[username]['pwd'] != hash:
                raise KeyError
        except KeyError:
            raise AuthenticationFailed

class ftp_server(threading.Thread):
    def __init__(self, host, port):
        super(ftp_server, self).__init__(name='ftp_server')
        self.authorizer = DummyMD5Authorizer()
        self.host = host
        self.port = port
       
    def run(self):
        self.handler = FTPHandler
        self.handler.log_prefix = '[FTP] %(remote_ip)s-[%(username)s]'
        self.handler.authorizer = self.authorizer
        self.address = (self.host, self.port)
        self.server = FTPServer(self.address, self.handler)
        self.server.serve_forever()

    def add_user(self,user,passwd,loc):
        self.authorizer.add_user(str(user), str(passwd), str(loc), perm='elradfmwM')

    def del_user(self,user):
        self.authorizer.remove_user(str(user))


class main(object):
    def __init__(self, ftp_host, ftp_port):
        self.run_ftp(ftp_host, ftp_port)
    
    def run_ftp(self, host, port):
        self.th_ftp = ftp_server(host, port)
        self.th_ftp.start()

class config(object):
    def __init__(self):
        self.config = 'config.yml'

    def create_config(self):
        with open(self.config, 'w') as f:
            raw_data = [{'global':{'ftp_host':'0.0.0.0','ftp_port':'21','user_config':'ftp.json'}}]
            with open(self.config, 'w') as f:
                yaml.dump(raw_data, f)

    def read_config(self):
        global public_data
        with open(self.config) as f:
            public_data = yaml.load(f, Loader=yaml.FullLoader)

class user_config(threading.Thread):
    def __init__(self):
        global public_data

        self.user = []

        with open(public_data[0]['global']['user_config'], 'r') as f:
            user_data = json.load(f)['sites']
        
        for i in range(len(user_data)):
            Main.th_ftp.add_user(user_data[i]['username'], user_data[i]['password'], user_data[i]['path'])
            self.user.append[user_data[i]['username']]
        
        self.check_updates()

    def check_updates(self):
        file_md5 = check_file_md5()
        while True:
            if (check_file_md5() != file_md5):
                # 更新 md5 值
                file_md5 = check_file_md5()
                # 检查变更的用户
                new_user = []

                with open(public_data['user_config'], 'r') as f:
                    user_data = json.loads(f)['sites']
        
                for i in len(user_data):
                    new_user.append[user_data[i]['username']]
                # 去除已删除部分
                for user in self.users:
                    if user not in new_user:
                        main.th_ftp.remove_user(user)
                # 添加新增部分
                i = 0
                for user in new_user:
                    if user not in self.users:
                        main.th_ftp.add_user(user, user_data[i]['password'], user_data[i]['path'])
                    i += 1
                # 覆盖新用户列表
                self.user = new_user
            print(self.user)
            time.sleep(1)


public_data = {}

if __name__ == "__main__":
    print('[I {}] [main] Checking file integrity...'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),))

    config_path = 'config.yml'
    # 若配置文件不存在，则创建空白配置文件
    if (os.path.exists(config_path)) == False:
        config().create_config()
    config().read_config()

    global_data = public_data[0]['global']
    Main = main(global_data['ftp_host'], global_data['ftp_port'])

    # 读取 FTP 配置文件
    th_user_config = user_config()
    th_user_config.start()