#!/bin/sh
Red="/etc/redhat-release"
Ubu="/etc/lsb-release"
Sys=""
Install_Result=""
Server=10.211.55.3
ListenIP=$1
Config=/etc/zabbix/zabbix_agentd.conf
exec >/test.log 2>&1
Red_Install()
{
	rpm -ivh http://repo.zabbix.com/zabbix/3.0/rhel/7/x86_64/zabbix-release-3.0-1.el7.noarch.rpm
	yum -y install zabbix-agent
	if [ $? -eq 0 ]; then
		Install_Result=0
	else
		echo "Install Error"
		rm $0
		exit 222
	fi
}

Ubu_Install()
{
	wget wget http://repo.zabbix.com/zabbix/3.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_3.0-1+xenial_all.deb
	dpkg -i zabbix-release_3.0-1+xenial_all.deb
	apt-get -y update
	apt-get -y install zabbix-agent
	if [ $? -eq 0 ]; then
		Install_Result=0
	else
		echo "Install Error"
		rm $0
		exit 222
	fi

}

if [ -e $Red ]; then
	Sys="Cen"

elif [ -e $Ubu ]; then
	Sys="Ubu"
	
else
	echo "This OS cann't install"
	rm $0
	exit 111
fi

netstat -ntlp|grep 10050
if [ $? -eq 0 ]; then
	echo 'zabbix-agent is running'
	rm $0
	exit 0
fi
case $Sys in
	'Cen' )
		Red_Install;;
	'Ubu' )
		Ubu_Install;;	
esac

if [ $Install_Result -eq 0 ]; then
	sed -i "s/^Server=.*$/Server=$Server/" $Config
	sed -i "s/#\ ListenIP=.*$/ListenIP=$ListenIP/" $Config
	systemctl enable zabbix-agent
	systemctl start zabbix-agent
	echo "Install Successfully"
else
	echo "Install Error"
fi
rm $0