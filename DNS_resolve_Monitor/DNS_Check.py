from dns import zone
from dns import resolver
from dns import rdatatype
from DNS_Check_mysql import Op_DB
from Send_Chat import Send_Mess_Chat
import re, hashlib, sys, time
Msg = []
Hash_ID_dict = {}
NS, MX, A, AAAA, SOA, TXT = ([] for i in range(6))
file1 = sys.argv[1:]

def Init_list(Cond,data):
    if Cond == 6:  # SOA
        SOA.extend(data)
    elif Cond == 2:  # NS
        NS.extend(data)
    elif Cond == 15:  # MX
        MX.extend(data)
    elif Cond == 1:  # A
        A.extend(data)
    elif Cond == 28:  # AAAA
        AAAA.extend(data)
    elif Cond == 16:
        TXT.extend(data)

def Check(rdt,data_list):
    for mid in data_list:
        if mid == 'freednsadmin.dnspod.com.' or mid == 'f1g1ns1.dnspod.net.' or mid == 'f1g1ns2.dnspod.net.' or mid == 'mxbiz1.qq.com.' or mid == 'mxbiz2.qq.com.':
            continue
        try:
            data1 = re.sub(mid, '',resolver.query(mid, rdt).rrset.to_text(), re.MULTILINE)
            x = re.findall('%s (?:\d+ )?([0-9a-zA-Z_:.]*)\.?'%rdt, data1)[0]
            ID_Hash = mid + "_" + rdt
            y = x.encode('utf8')
            Hash_ID_dict[ID_Hash] = [str(hashlib.md5(y).hexdigest()), x]
        except Exception as e:
            time.sleep(10) 
            try:
                data1 = re.sub(mid, '',resolver.query(mid, rdt).rrset.to_text(), re.MULTILINE)
                x = re.findall('%s (?:\d+ )?([0-9a-zA-Z_:.]*)\.?'%rdt, data1)[0]
                ID_Hash = mid + "_" + rdt
                y = x.encode('utf8')
                Hash_ID_dict[ID_Hash] = [str(hashlib.md5(y).hexdigest()), x]
            except Exception as e:
                Msg.append("Domain name: %s\nReason: %s" %(mid, e))


if __name__ == '__main__':
    for file_name in file1:
        with open(file_name,'r') as f:
            ZD = zone.from_file(f)
            f.close()
        for Name,Datarest in ZD.iterate_rdatasets():
            if str(Name) == '@':
                Init_list(1, re.findall('.*? ([a-zA-Z0-9]{1,}\..*?\.[a-zA-Z0-9]{1,}.[a-zA-Z0-9]{0,}[.a-zA-Z0-9]{0,})',\
                                                      Datarest.to_text(), \
                                                      re.MULTILINE))
            else:
                list_2 = []
                list_2.append(Name.to_text() + '.' + ZD.origin.to_text())
                Init_list(Datarest.rdtype, list_2)
        NS.extend([ZD.origin.to_text(), 'NS'])
        SOA.extend([ZD.origin.to_text(), 'SOA'])
        MX.extend([ZD.origin.to_text(), 'MX'])
        A.append('A')
        AAAA.append('AAAA')
        TXT.extend([ZD.origin.to_text(), 'TXT'])
        for i in  NS, MX, A, AAAA, SOA, TXT:
            Check(i[-1], i[:-1])
        if len(Msg) != 0:
        #    print('\n'.join(Msg))
            Send_Mess_Chat('\n'.join(Msg), 'DNS解析失败')
    
        test = Op_DB()
        table_name = re.sub('\.','_',ZD.origin.to_text())+'zone'
        test.Check_Hash_is_exist(table_name, **Hash_ID_dict)
