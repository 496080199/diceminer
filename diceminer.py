from pyeoskit import db
from pyeoskit import eosapi
from pyeoskit import wallet
import os,random


nodes=[
'http://jungle.cryptolions.io:18888',
'http://dev.cryptolions.io:38888',
]
eosapi.set_nodes(nodes)
ref='cljcljcolden'


def mkrandstr():
    randstr=''
    for i in range(18):
        randstr+=random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890')
    return randstr

def bet(account,amount,token,rollmin,rollmax):
    if token=='EOS':
        acacount='eosio.token'
    elif token=='EBTC' or token=='EUSD' or token =='EETH':
        acacount='bitpietokens'
    else:
        acacount=''
        print('币种不存在,退出')
        exit(0)
    authorization = {account: 'active'}
    memo='action:bet,seed:' + mkrandstr() + ',rollUnder:' + random.randint(rollmin,rollmax) + ',ref:' + ref
    data={
        "from":account,
        "to":'betdiceadmin',
        "quantity": '%.4f'%amount+" "+token,
        "memo": memo
    }

    betaction=[acacount,'transfer',data,authorization]
    return eosapi.push_action(*betaction)

def main():
    if not os.path.exists('eoswallet'):
        psw=wallet.create('eoswallet')
        print('您的EOS钱包密码为：' + psw + '，请务必妥善保管，否则无法打开钱包。')
        wallet.unlock('eoswallet', psw)
        secret=input('请输入账号的操作私钥，导入钱包中，本程序不会记录您的私钥')
        wallet.import_key('eoswallet', secret)
        wallet.lock('eoswallet')


    pass

if __name__ == '__main__':
    main()