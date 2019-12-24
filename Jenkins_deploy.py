import wget
import os
import request
import hashlib


def has_new_ver(ver_url, ver_file_name):
	# 有最新版本返回true，否则返回false

	# 没有版本文件，表示没有新版本
	if not os.path.isfile(ver_file_name)
		return True

	# 本地版本号
	with open(ver_file_name) as local_ver_file:
		local_ver = local_ver_file.read()

	# Jenkins最新版本
	remote_ver = request.get(ver_url).text
	
	# 有最新版本
	if local_ver != remote_ver:
		return True
	else
		return False


def file_ok(md5_url, app_file_name):
	# md5检测文件是否损坏，损坏返回false
	m = hashlib.md5()
	# 计算本地文件的md5值
	with open(app_file_name, "rb") as fd:
		while 1:
			data = fd.read(4096)
			if not data:
				break;
			m.update(data)

	# Jenkins上,软件对应的md5
	remote_md5 = request.get(md5_url).text.strip()

	if m.hexdigest() == remote_md5:
		return True
	else
		return False


def deploy(app_file_name):
	# 部署
	# tar包解压缩到这个目录
	deploy_dir = "/var/www/deploy"
	# 解压
	tar = tarfile.open(app_file_name)
	tar.extractall(path = deploy_dir)
	tar.close()

	# 目录名 /var/www/deploy/website-1.0
	app_dir = app_file_name.split("/")[-1].replace("tar.gz", "")
	app_dir = op.path.join(deploy_dir, app_dir)

	# 快捷方式
	dest = "/var/www/html/mypro"
	if os.path.exists(dest):
		os.remove(dest)

	# ln -s /var/www/deploy/website-1.0 /var/www/html/mypro
	os.link(app_dir, dest)


def main():

	# 判断是否有最新版本
	# jenkins服务器上的最新版本所在的地址
	ver_url = "http://192.168.1.82/deploy/live_ver"
	# 本地软件版本号所在目录
	ver_file_name = "/var/www/deploy/live_ver"

	if not has_new_ver(ver_url, ver_file_name):
		print("未发现新版本")
		exit(1)


	# 下载软件
	# 获取最新版本
	remote_ver = request.get(ver_url).text.strip()
	# Jenkins上，软件包
	app_url = "http://192.168.1.82/deploy/pkgs/website-" + remote_ver + "tar.gz"
	# 本地下载目录
	down_dir = "/var/www/download"
	wget.download(app_url, down_dir)


	# 检测文件是否损坏
	# Jenkins上，md5文件
	md5_url = app_url + ".md5"
	# 软件名		website-xxx.tar.gz
	app_file_name = app_url.split("/")[-1]
	# 本地文件的绝对路径
	app_file_name = os.path.join(down_dir, app_file_name)
	
	if not file_ok(md5_url, app_file_name):
		os.remove(app_file_name)
		print("文件损坏")
		exit(2)


	# 部署
	deploy(app_file_name)


	# 更新live_ver文件，删除再下载
	if os.path.exists(ver_file_name):
		os.remove(ver_file_name)
	wget.download(ver_url, ver_file_name)

if __name__ == '__main__':
	main()