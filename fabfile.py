# -*- coding: utf-8 -*-

from fabric.api import *
import os


env.hosts=['35.198.76.72']
env.user='jose-luis'
env.key_filename='/home/jose-luis/.ssh/coreKeys/jose-luis'
env.roledefs={'stage':['35.198.76.72'],
                'production': [''],                                 
               }
env.disable_known_hosts = False
env.reject_unknown_hosts = False

def whoAmI():
    run('uname -a')
    run ('whoami')
    
def updateMachine():
    run('sudo apt-get update')

def installUtilities():
    run('yes | sudo apt-get install gcc g++ make git cmake rename')
    
def installGnomeAndVNC():
    run('yes | sudo apt-get install expect tightvncserver autocutsel xfce4 xfce4-goodies git-cola')
    run('wget https://download.netbeans.org/netbeans/8.2/final/bundles/netbeans-8.2-cpp-linux-x64.sh && chmod +x netbeans-8.2-cpp-linux-x64.sh')
#run('yes | sudo apt-get install gcc g++ make git cmake')    when no gui is needed gnome-core gnome-panel
        
def getINCA():
    run('''mkdir -p keys''')
    put('~/.ssh/Lecheps', './keys/Lecheps') 
    run(' '.join('''if [ ! -d ./INCA ];
                    then
                        eval `ssh-agent -s`
                        chmod 600 ./keys/Lecheps &&
                        ssh-add ./keys/Lecheps &&
                        ssh-keyscan github.com >> ~/.ssh/known_hosts &&
                        yes | git clone ssh://git@github.com/biogeochemistry/INCA.git &&                    
                        cd INCA &&
                        git checkout 47378b13f7c7d2a3945611d2fb9b8b4233aad54e;
                    fi
           '''.replace('\n', ' ').split())
        )
#gcloud source repos clone INCA &&    
#b6ef28a302244e59e9283a4e41d575b4aae83dfa fixed modular building  
#228688e6422bb62e3b4ee8b48f0294c7a43d6d59 

def getTinyxml2():
    run(' '.join('''if [ ! -d ./tinyxml2 ];
                    then 
                        git clone https://github.com/leethomason/tinyxml2.git;
                    fi
           '''.replace('\n', ' ').split())
       )

def getBoost(boostLink):
    filename = boostLink.rsplit('/', 1)[-1]
    filename = filename[:-1]
    cmd = '''if [ ! -d ./boost ];
             then 
                 wget {0} && tar -xf {1} && rm {1}; 
             fi
           '''
    runCmd = cmd.format(boostLink,filename)
    run( ' '.join(runCmd.replace('\n',' ').split()) )    


def getSqlite(sqliteLink):
    filename = sqliteLink.rsplit('/', 1)[-1]
    filename = filename[:-1]
    cmd = '''if [ ! -d ./sqlite ];
             then 
                 wget {0} && tar -xf {1} && rm {1} && mv sqlite* sqlite; 
             fi
           '''
    runCmd = cmd.format(sqliteLink,filename)
    run( ' '.join(runCmd.replace('\n',' ').split()) )      
    
    
def addINCAToPath():
    run('''echo 'export COREDIR=~/INCA' >> ~/.profile ''')
    
def compileBoost():
    run('''export BOOST=$(ls -t -U | grep -m 1 "boost") &&
           echo $BOOST &&
           cd $BOOST &&
           ./bootstrap.sh &&
           ./b2 toolset=gcc link=static,shared --with-regex --with-system --with-filesystem --with-date_time &&
           sudo cp -a ./stage/lib/. /usr/local/lib
        '''
       )

def compileTinyxml2():
    run('''export TINY=$(ls -t -U | grep -m 1 "tiny") &&
           cd $TINY &&
           mkdir build && cd build &&
           cmake .. -DBUILD_SHARED_LIBS:BOOL=OFF -DBUILD_STATIC_LIBS:BOOL=ON &&
           make &&
           sudo cp libtinyxml2.a /usr/local/lib
        '''
       )

def compileCore():
    #capitalizing utility.h in all files so the (case sensitve) includes don't break
    #removing spaces in all file names and directories within the INCA directory
    run('''
           find ./INCA -type f -exec sed -i 's/include "utility.h"/include "Utility.h"/g' {} \; &&
           find ./INCA/ -depth -name "* *" -execdir rename 's/ /_/g' "{}" \; &&
           cd ./INCA &&
           sed -i s/^CND_DLIB_EXT=.*/CND_DLIB_EXT=so/ Makefile &&
           make &&
           make install &&
           sed -i s/^CND_DLIB_EXT=.*/CND_DLIB_EXT=a/ Makefile &&
           make clean &&
           make &&
           make install
        '''
       )

def compileExamples():
     run('''chmod +x compileExamples.sh && ./compileExamples.sh''')

def compileTests():
    run('''chmod +x compileTests.sh && ./compileTests.sh''')

def setLibPath():
    run('''echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/:/home/{0}/local/lib" >> /home/{0}/.bashrc
        '''.format(env.user)
       )
    
def setBinPath():
    run('''echo "export PATH=$PATH:/home/{0}/local/bin" >> /home/{0}/.profile
        '''.format(env.user)
       )

def getPip():
    run('yes | sudo apt-get install python-pip')

def getModules():
    run('sudo pip install xmlstore editscenario xmlplot matplotlib')

def initVNC(password):
    put('./vnc.exp','vnc.exp')
    run('''chmod +x ./vnc.exp &&
           ./vnc.exp ''' + password + ''' &&
           vncserver -kill :1
        '''   
        )   
def setupVNC():
    put('./xstartup','~/.vnc/xstartup')
    run('''chmod +x ~/.vnc/xstartup 
        '''
       )
# &&
#            touch ./Xresources &&
#            chmod +x ./Xresources
    
    
    
def startVNC():
    run('''if [ -f ~/.vnc/*:1.pid ];
           then
               vncserver -kill :1;
           fi &&
           vncserver -geometry 1980x1200 -depth 16
        ''', pty=False
       )
#def startVNC():
#    run('vncserver -geometry 1980x1200 -depth 16', pty=False)
    
@task
def testConnection():
    whoAmI.roles=('stage',)
    execute(whoAmI)

@task
def update():
    updateMachine.roles=('stage',)
    execute(updateMachine)

@task
def getUtilities():
    updateMachine.roles=('stage',)
    installUtilities.roles=('stage',) 
    getPip.roles=('stage',)
    getModules.roles=('stage',)
    execute(update)
    execute(installUtilities)
    #execute(getPip)
    #execute(getModules)
 
@task
def getGnomeAndVNC(vncPassword):
    updateMachine.roles=('stage',)
    installGnomeAndVNC.roles=('stage',)
    initVNC.roles=('stage',)
    setupVNC.roles=('stage',)
    
    execute(updateMachine)
    execute(installGnomeAndVNC)
    execute(initVNC,vncPassword)
    execute(setupVNC)
    

@task
def downloadSources(boostLink,sqliteLink):
    getINCA.roles=('stage',)
    addINCAToPath.roles=('stage',)
    getTinyxml2.roles=('stage',)
    getBoost.roles=('stage',)
    getSqlite.roles=('stage',)
    execute(getINCA)
    execute(addINCAToPath)
    execute(getTinyxml2)
    execute(getBoost,boostLink)    
    execute(getSqlite,sqliteLink)
    
@task
def compileModels():
    put('./Makefile','./INCA/Makefile') 
    compileBoost.roles=('stage',)
    compileTinyxml2.roles=('stage',)
    compileCore.roles=('stage',)
    execute(compileBoost)
    execute(compileTinyxml2)
    execute(compileCore)
    
@task
def examples():
    put('./Makelib','.')
    put('./compileExamples.sh','.')
    compileExamples.roles=('stage',)
    execute(compileExamples)
    
@task
def tests():
    put('./Maketests', '.')
    put('./compileTests.sh', '.')
    compileTests.roles=('stage',)
    execute(compileTests)
        
@task
def startVNCServer():
    startVNC.roles=('stage',)
    execute(startVNC)
    
@task 
def setEnv():
    setLibPath.roles=('stage',)
    setBinPath.roles=('stage',)
    execute(setLibPath)
    execute(setBinPath)

