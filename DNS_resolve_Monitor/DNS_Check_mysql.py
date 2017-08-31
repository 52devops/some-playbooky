from Send_Chat import Send_Mess_Chat
import pymysql
import re

class Op_DB(object):
    """docstring for """

    def __init__(self, Server_host='localhost', DB_user='DNS', DB_passwd='123', DB_name='DNS_Check'):
        try:
            self.conn1 = pymysql.connect(host=Server_host, user=DB_user, passwd=DB_passwd, db=DB_name)
        except Exception:
            print('Connect DB failed')
        self.cur = self.conn1.cursor()
        self._ID_HASH_CHANGED = []
        self._MSG = []

    def Insert_Data(self, tab_name, *args):
        sql = re.sub('\%s', tab_name,
                     "insert into %s (ID_HASH, Value) VALUES(%s,%s)", count=1)
        self.cur.executemany(sql, args)
        self.conn1.commit()
        self.conn1.close()

    def Check_Hash_is_exist(self, tab_name, **kwargs):
        '''
            kwargs.key is ID_Hash(Name) of table
            kwargs.Value is Value(hash) of table

        '''
        data = [(tab_name, x) for x in kwargs.keys()]
        try:
            for i in data:
                sql = "select ID_HASH from %s WHERE ID_HASH='%s'" % i
                b = self.cur.execute(sql)
                if b == 0:
                    self._ID_HASH_CHANGED.append(data[1])
                    self._ADD_ID_HASH(tab_name, **kwargs)
                else:
                    self._Check_Value(tab_name, i[1], **kwargs)
            self.conn1.close()
            self.Send()
        except pymysql.err.InterfaceError:
            print('Close conn')
            self.conn1.close()

    def _ADD_ID_HASH(self, tab_name, **kwargs):
        '''
            传入字典，查询的域名为key,dataset为value.
        '''
        self._Updata_DATA = [(k, v[0]) for k, v in kwargs.items()]
        self.Insert_Data(tab_name, *self._Updata_DATA)

    def _Check_Value(self, tab_name, ID_hash_name, **kwargs):
        '''
            为已存在的值，检测其Value是否变更
            args[0] is a tuple,
            args[0][0] is table_name
            args[0][1] is ID_Hash
        '''

        sql = "select Value from %s WHERE ID_HASH='%s'" % (
            tab_name, ID_hash_name)
        self.cur.execute(sql)
        if kwargs[ID_hash_name][0] == self.cur.fetchone()[0]:
            pass
        else:
            self._Updata_Value(tab_name, ID_hash_name, **kwargs)

    def _Updata_Value(self, tab_name, ID_hash_name, **kwargs):
        '''
            更新改变的Value
        '''
        sql = "update %s set Value='%s' WHERE ID_HASH='%s'" % (
            tab_name,
            kwargs[ID_hash_name][0],
            ID_hash_name)
        self.cur.execute(sql)
        self.conn1.commit()
        mid_msg = ID_hash_name.split('_')
        self._MSG.append('The %s %s Responder is changed to %s' %(mid_msg[0] , mid_msg[1], kwargs[ID_hash_name][1]))

    def Send(self):
        #print('\n'.join(self._MSG))
        Send_Mess_Chat('\n'.join(self._MSG), 'DNS解析变动通知')
