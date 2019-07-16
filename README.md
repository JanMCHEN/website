# website
django learn
django 搭建个人博客网站，nginx负载均衡在两台服务器上有部署，支持注册、登录、写博客、点赞、收藏、上传头像、ip代理池获取、发图、评论等，集成百度ueditor编辑器，fastdfs分布式存储、haystack全文搜索

部署过程：

系统编码：
echo 'export LANG="en_US.UTF-8' >> ~/.bash_profile

| pyenv:
debian ubantu依赖：
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
centos依赖：
sudo yum install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel findutils gcc gcc-c++ git make wget net-tools
安装：
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
以下bashrc在centos里是bash_profile
echo 'export PATH=~/.pyenv/bin:$PATH' >> ~/.bashrc
echo 'export PYENV_ROOT=~/.pyenv' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

echo 'export PATH=~/.pyenv/bin:$PATH' >> ~/.bash_profile
echo 'export PYENV_ROOT=~/.pyenv' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile
virtual：
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
用：
pyenv virtualenv 3.6.4 env-3.6.4 # 创建3.6.4版本的虚拟环境


# 时区
timedatectl set-timezone Asia/Shanghai
timedatectl status
# 编码
echo 'export LANG=en_US.UTF-8' >> ~/.bash_profile
---------------------------------------------------------------
pip freeze > requirements.txt
pip install -r 路径

#centos7开端口
那怎么开启一个端口呢
添加
firewall-cmd --zone=public --add-port=80/tcp --permanent    （--permanent永久生效，没有此参数重启后失效）
重新载入
firewall-cmd --reload
查看
firewall-cmd --zone=public --query-port=80/tcp
删除
firewall-cmd --zone=public --remove-port=80/tcp --permanent


mysql（centos7）：
添加源安装启动：
wget https://dev.mysql.com/get/mysql57-community-release-el7-9.noarch.rpm
rpm -ivh mysql57-community-release-el7-9.noarch.rpm
yum install mysql-server
systemctl start mysqld #启动MySQL
grep 'temporary password' /var/log/mysqld.log #获取临时密码
systemctl enable mysqld #设置开机启动
基本操作：
set password='';		#重设密码
CREATE USER 'django'@'localhost' IDENTIFIED BY 'passwd';	添加用户django
CREATE DATABASE if not exists django DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;	#新建数据库
GRANT all ON test.* TO 'django'@'localhost'; 	test数据库所有权限
FLUSH PRIVILEGES; 			#刷新权限



redis：
yum install redis
redis-server /etc/redis.conf		#需要修改daemonize yes允许后台运行   requirepass passwd设置密码
redis-cli				#连接        keys *	显示所有键 auth passwd验证密码





fastdfs:(阿里轻量无法直接绑定公网ip）
git clone https://github.com/happyfish100/libfastcommon.git
git clone https://github.com/happyfish100/fastdfs.git
然后分别cd到目录  ./make.sh  
		./make.sh install
配置tracker:  /etc/fdfs/
base_path=/home/mm/fastdfs/tracker  #tracker存储data和log的跟路径，必须提前创建好 mkdir -p
http.server_port=80 #http端口，需要和nginx相同
fdfs_tracker /etc/fdfs/tracker.conf [start stop]   #启动停止
配置storage：
base_path=/home/mm/fastdfs/storage   #storage存储data和log的跟路径，必须提前创建好
port=23000  #storge默认23000，同一个组的storage端口号必须一致
group_name=group1  #默认组名，根据实际情况修改
store_path_count=1  #存储路径个数，需要和store_path个数匹配
store_path0=/home/mm/fastdfs/storage  #如果为空，则使用base_path
tracker_server=10.122.149.211:22122 #配置该storage监听的tracker的ip和port
fdfs_storaged /etc/fdfs/storage.conf start
配置client:
base_path=/home/mm/fastdfs/client/
tracker_server=10.122.149.211:22122 #配置该storage监听的tracker的ip和port
fdfs_upload_file /etc/client.conf test.txt			#返回group*则连接成功
开机启动：
chkconfig fdfs_trackerd on
chkconfig fdfs_storaged on

nginx：
git clone https://github.com/happyfish100/fastdfs-nginx-module.git  #模块
wget http://nginx.org/download/nginx-1.15.10.tar.gz
tar -zxvf 
cd
./configure --prefix=/usr/local/nginx --add-module=(fastdfs-nginx绝对路径)src/
make
make install		#在上面指定的/usr/local/nginx下
cp fdfsmodule下的src/mod_fastdfs.conf 	和/root/fastdfs/conf下的http.conf mime.types   到/etc/fdfs/
修改mod_fastdfs.conf以下内容为：
base_path=存放日志
storage_path0=和storage路径相同
http_server=ip:port同storage
url_have_group_name=url里带不带group
# nginx 配置
负载均衡
upstream machine { 
      server 139.224.13.15 weight=5; 
      server 64.190.202.73 weight=1; 
}
server {
	listen 8888;
	server_name _;
	location ~/group[0-9]/ {
	ngx_fastdfs_module;
	}
	error_page   500 502 503 504  /50x.html;
        	location = /50x.html {
            	root   html;
        	}
}

location /static {
	# 静态文件
	alias /www/myweb/static/;
}

python连接：
pip install py3Fdfs
事例：
from fdfs_client.client import *
client_conf_obj = get_tracker_conf('/etc/fdfs/client.conf')
client = Fdfs_client(client_conf_obj)
ret = client.upload_by_filename('test')


uwsgi配置：   （加入到开机启动项：echo "uwsgi -c /usr/local/nginx/conf/nginx.conf" >> /etc/rc.local
[uwsgi]
#使用nginx连接时使用
;socket=127.0.0.1:8080
#直接做web服务器使用 相当于 python manage.py runserver ip:port
http=127.0.0.1:8000
# 项目目录
chdir=/www/
# 项目中wsgi.py文件的目录，相对于项目目录
wsgi-file=mysite/wsgi.py
# 指定工作的进程数
processes=4
# 指定工作进程中的线程数
threads=2
# 主进程
master=true
# 保存启动之后主进程的pid,用于脚本启动、停止该进程
pidfile=uwsgi.pid
# 设置uwsgi后台运行，保存日志信息
daemonize=uwsgi.log
# 设置虚拟环境的路径
virtualenv=/root/.pyenv/versions/3.6.8/envs/Dweb
env = LANG=en_US.UTF-8









开机自启：(注意.local权限）
nginx：		echo "/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf" >> /etc/rc.local
	或者vim /usr/lib/systemd/system/nginx.service， 记住 systemctl daemon-reload
[Unit]
Description=nginx - high performance web server
After=network.target remote-fs.target nss-lookup.target
[Service]
Type=forking
PIDFile=/usr/local/nginx/logs/nginx.pid
ExecStartPre=/usr/local/nginx/sbin/nginx -t -c /usr/local/nginx/conf/nginx.conf
ExecStart=/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
ExecReload=/usr/local/nginx/sbin/nginx -s reload
ExecStop=/usr/local/nginx/sbin/nginx -s stop
ExecQuit=/usr/local/nginx/sbin/nginx -s quit
PrivateTmp=true
[Install]
WantedBy=multi-user.target

