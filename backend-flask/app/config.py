import os
import configparser

class Config:
    SECRET_KEY='The Last of Us'
    settingsfile='./configuration/openehrtool.cfg'

def get_config():
    settingsfile=Config.settingsfile
    #get vars from env
    env_varset = [os.environ.get('EHRBASESERVER_nodename', None),
                  os.environ.get('REDISSERVER_hostname', None),
                  os.environ.get('REDISSERVER_port', None),]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    settingsfile = os.path.join(current_dir, settingsfile)
    if (os.path.exists(settingsfile)):
        print(f"Reading settings from {settingsfile}")
        varset=readconfigfromfile(settingsfile)
        #build varset from environment variables
        for i in ([0,1,2]):
            if env_varset[i] is None:
                env_varset[i] = varset[i]
    varset = tuple(env_varset)
    nodename,redishostname,redisport=varset        
    return nodename,redishostname,redisport

def readconfigfromfile(filename):
    print('readconfigfromfile------------------------------')
    config = configparser.ConfigParser()
    config.read(filename)
    nodename=config['EHRBASESERVER']['nodename']
    redishostname=config['REDISSERVER']['hostname']
    redisport=config['REDISSERVER']['port']
    return nodename,redishostname,redisport