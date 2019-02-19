from pyeoskit import eosapi
from pyeoskit import wallet
from configparser import ConfigParser
from pytz import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.interval import IntervalTrigger
import os,random,getpass,datetime
import typing
import logging
from logging.handlers import RotatingFileHandler,TimedRotatingFileHandler


log=logging.getLogger()
log.setLevel(logging.WARN)
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = TimedRotatingFileHandler(filename='diceminer.log', when='midnight', interval=1, backupCount=15, encoding='UTF-8')
h.setFormatter(fmt)
log.addHandler(h)

tz=timezone('Asia/Shanghai')


ref='cljcljcolden'


def createwallet():
    eoswallet = 'eoswallet'
    if not os.path.exists(eoswallet+'.wallet'):
        psw = wallet.create(eoswallet)
        print('首次使用需导入私钥创建钱包')
        print('您的EOS钱包密码为：' + psw + '，（重要！重要！重要！)请务必妥善保管，否则无法打开钱包。\n')
        accept = input('确认请输入yes或y（回车结束）:\n')
        if accept == 'yes' or accept == 'y':
            pass
        else:
            os.remove(eoswallet + '.wallet')
            os._exit(0)
        wallet.unlock(eoswallet, psw)
        secret = getpass.getpass('\n请输入账号的操作私钥（回车结束），导入钱包中，程序不会记录您的私钥:\n')
        importresult=wallet.import_key(eoswallet, secret)
        if importresult:
            print('钱包导入私钥成功,请重新运行即可\n')
            wallet.save(eoswallet)
            wallet.lock(eoswallet)
            os._exit(0)
        else:
            os.remove(eoswallet+'.wallet')
            print('私钥导入错误，请重新运行再尝试\n')
            os._exit(0)




def getdatetime():
        dt=datetime.datetime.now(tz).isoformat()
        return dt


def mkrandstr():
    randstr=''
    for i in range(18):
        randstr+=random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890')
    return str(randstr)

def bet(psw,account,amount,token,rollmin,rollmax):
    log.warning('###DICE投注开始###')
    if token=='EOS':
        acacount='eosio.token'
    elif token=='EBTC' or token=='EUSD' or token =='EETH':
        acacount='bitpietokens'
    elif token=='DICE':
        acacount='betdicetoken'
    else:
        acacount=''
        print('币种不存在,退出')
        os._exit(0)
    authorization = {account: 'active'}
    randnum=random.randint(rollmin,rollmax)
    memo='action:bet,seed:' + mkrandstr() + ',rollUnder:' + str(randnum) + ',ref:' + str(ref)
    data={
        "from":account,
        "to":'betdiceadmin',
        "quantity": '%.4f'%amount+" "+token,
        "memo": memo
    }

    betaction=[acacount,'transfer',data,authorization]
    log.warning('#投注账号：'+str(account)+',本次投注：'+'%.4f'%amount+" "+token+',投注小于数字：'+str(randnum))
    wallet.open('eoswallet')
    wallet.unlock('eoswallet',psw)
    log.warning('投注时间：'+str(getdatetime()))
    result=eosapi.push_action(*betaction)
    wallet.lock('eoswallet')
    log.warning('投注记录：\n'+str(result))

def main():
    print('欢迎使用diceminer\n'
          '本程序基于DICE平台的骰子游戏开发的自动化投注工具，可设定投注数字范围随机投注，支持EOS,EBTC,EETH,EUSD,DICE币种，按时间间隔\n'
          '投注，具体查看config.ini配置文件。程序自带钱包功能，通过钱包密码保护私钥安全，为确保更安全，建议开设独立的EOS账号运行程序。\n'
          '步骤：1.根据需要配置config.ini(UTF-8编码) 2.启动生成钱包密码并导入操作私钥到钱包 3.重启即开始运行投注\n'
          '有问题可加入telegram电报群讨论:https://t.me/dice1_zh，我的tg号：xiaopao\n\n')
    scheduler = BlockingScheduler(timezone=tz)
    psw=''
    cfg = ConfigParser()
    if os.path.exists('config.ini'):
        cfg.read('config.ini', encoding="utf-8")
        net = cfg.get('miner', 'net')
        interval = cfg.getint('miner', 'interval')
        account = cfg.get('miner', 'account')
        amount = cfg.getfloat('miner', 'amount')
        token = cfg.get('miner', 'token').upper()
        rollmin = cfg.getint('miner', 'rollmin')
        rollmax = cfg.getint('miner', 'rollmax')
    else:
        env_dist = os.environ
        net = env_dist['NET']
        interval = env_dist['INTERVAL']
        account = env_dist['ACCOUNT']
        amount = env_dist['AMOUNT']
        token = env_dist['TOKEN']
        rollmin = env_dist['ROLLMIN']
        rollmax = env_dist['ROLLMAX']
        psw = env_dist['PSW']


    nodes = [
        net,
    ]
    eosapi.set_nodes(nodes)

    createwallet()
    print('注：如已忘记钱包密码，可删除.wallet文件，重新导入私钥')
    if os.path.exists('config.ini'):
        psw = getpass.getpass('请输入您的钱包密码（回车结束）：\n')

    mywallet = wallet.unlock('eoswallet', psw)
    if mywallet:
        pass
    else:
        print('钱包密码错误，请重试\n')
        os._exit(0)

    if interval < 1:
        print ('投注间隔为整数，且最小为1秒')
        os._exit(0)
    trigger = OrTrigger([
        IntervalTrigger(seconds=interval)
    ])

    if token == 'EOS':
        if amount < 0.1:
            print('投注EOS金额必须大于等于0.1')
            os._exit(0)
    elif token == 'EBTC':
        if amount < 0.0001:
            print('投注EBTC金额必须大于等于0.0001')
            os._exit(0)
    elif token == 'EETH':
        if amount < 0.001:
            print('投注EETH金额必须大于等于0.001')
            os._exit(0)
    elif token == 'EUSD':
        if amount < 0.1:
            print('投注EUSD金额必须大于等于0.1')
            os._exit(0)
    elif token == 'DICE':
        if amount < 10.0:
            print('投注DICE金额必须大于等于10.0')
            os._exit(0)

    if rollmin < 2 or rollmax > 96 or rollmin >= rollmax:
        print('投注数字大小范围为2-96，设置错误')
        os._exit(0)
    scheduler.add_job(bet, trigger, name='bet',
                      id='bet',
                      args=[psw,account,amount,token,rollmin,rollmax])
    print('投注任务已启动,每隔'+str(interval)+'秒执行一次，请保证EOS账号内CPU资源充足，执行详情请查看diceminer.log日志文件,结束运行请关闭窗口')
    #scheduler.print_jobs()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == '__main__':
    main()