# -*- coding: utf-8 -*-

from fabric.api import *
import os


env.hosts=['35.234.105.210']
env.user='jose-luis'
env.key_filename='/home/jose-luis/.ssh/coreKeys/jose-luis'
env.roledefs={'stage':['35.234.105.210'],
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
    run('yes | sudo apt-get install gcc g++ make git cmake')
        
def getINCA():
    run(' '.join('''if [ ! -d ./INCA ];
                    then 
                        gcloud source repos clone INCA &&
                        cd INCA &&
                        git checkout b6ef28a302244e59e9283a4e41d575b4aae83dfa;
                    fi
           '''.replace('\n', ' ').split())
        )
    
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
    run('''
           find ./INCA -type f -exec sed -i 's/include "utility.h"/include "Utility.h"/g' {} \; && 
           cd ./INCA &&
           make &&
           sudo make install
        '''
       )    

def getPip():
    run('yes | sudo apt-get install python-pip')

def getModules():
    run('sudo pip install xmlstore editscenario xmlplot matplotlib')   
    
def changeScenarioInXML(oldScenario,newScenario,file):
    run('''xmlstarlet ed --inplace -u "scenario[@version='{}']/@version" -v '{}' {}'''.format(oldScenario,newScenario,file))

def setSchemaDir(filename):
    scenarioFile = os.path.split(filename)[0] + '/editscenario.sh'
    run(''' 'sed -i 's_\(--schemadir=.*\s\)_--schemadir="$GOTMDIR"/schemas _g' {}'''.format(scenarioFile))

def editScenario(filename):
    #run("tail ~/.profile")
    #run('echo $GOTMDIR')
    run('''cd "$(dirname {})" && editscenario --schemadir "$GOTMDIR"/schemas -e nml . langtjern.xml'''.format(filename))

def runGOTM(filename):
    run('cd "$(dirname "{}")" && gotm'.format(filename));
        

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
    execute(getPip)
    #execute(getModules)

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
    #compileGOTM.roles=('stage',)
    #installGOTM.roles=('stage',)
    #execute(compileFABM)
    #execute(compileGOTM)
    #execute(installGOTM)

@task
def testRun(filename):
    changeScenarioInXML.roles=('stage',)
    setSchemaDir.roles=('stage',)
    editScenario.roles=('stage',)
    runGOTM.roles=('stage',)
    
    changeScenarioInXML('gotm-5.1','gotm-5.3',filename)
    #setSchemaDir(filename)
    editScenario(filename)
    runGOTM(filename)
