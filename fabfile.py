import os, sys, re
from os.path import expanduser
from fabric.context_managers import cd
from fabric.contrib.console import confirm
from fabric.operations import prompt
from fabric.operations import run
from fabric.colors import green
from fabric.api import *

home = os.path.expanduser('~')

@task(default=True)
def install(manager="conda"):
    update()
    python(manager)
    docker()

@task
def python(manager="conda"):
    """
    Install all the Python packages
    """
    print(green("Installing Python packages..."))
    if manager == "conda":
        local('conda config --set always_yes TRUE')
        local('conda install pandas')
        local('conda install pymongo')
        local('conda install pysam')
        local('conda install ujson')
        local('conda install tornado')
        local('pip install docker') #conda not working
    elif manager == "pip":
        local('pip install pandas')
        local('pip install pymongo')
        local('pip install pysam')
        local('pip install ujson')
        local('pip install tornado')
        local('pip install docker')
    else:
        print ("You need to install the following Python packages:")
        print ("pandas")
        print ("pymongo")
        print ("pysam")
        print ("ujson")
        print ("tornado")
        print ("docker")

@task
def website():
    """
    Install the website
    """
    print(green("Installing the website dependencies..."))
    print(green("You need to have node.js installed on your computer (https://nodejs.org/en/)."))

    if sys.platform != 'darwin': #if not OSX
        print(green("Installing Node.js..."))
        local("sudo apt-get -y install nodejs npm")
        local("sudo ln -sf `which nodejs` /usr/bin/node")

    print(green("Installing Bower..."))
    local("sudo npm install -g bower")

    print(green("Installing the website..."))
    local('cd website ; bower --config.interactive=false install')

@task
def mongodb():
    """
    Install MongoDB
    """
    print(green("Installing MongoDB..."))

    if sys.platform != 'darwin': #if not OSX
        local("sudo apt install mongodb-server")

@task
def docker():
    """
    Install the Docker images
    """
    local('docker pull fjossinet/assemble2')
    local('docker pull fjossinet/rnaseq')

@task
def jupyter(manager="conda"):
    """
    Install Jupyter
    """
    if manager == "conda":
        local("conda install jupyter")
    elif manager == "pip":
        local("pip install jupyter")
    else:
        print ("You need to install Jupyter(http://jupyter.org)")

def update():
    """
    Update the operating system
    """
    if sys.platform != 'darwin': #if not OSX
        print(green("Using Linux..."))
        print(green("Updating the package list..."))
        local('sudo apt-get update -qq')
    #else:
    #    print(green("Using MacOSX"))
    #    with warn_only():
    #        local('brew update')

def bcheck(installation_directory = "%s/algorithms"%home):
    """
    Install BCheck
    """
    print(green("Installing BCheck..."))
    if not os.path.exists('%s/Bcheck/'%installation_directory):
        local('echo "export PATH=\$PATH:%s/Bcheck/" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/Bcheck-0.6/'%installation_directory):
        with lcd(installation_directory):
            #the Bcheck recovered from Dropbox has been modified to not check the rnabob and Infernal version
            local('wget -qO Bcheck-0.6.tar.gz http://dl.dropbox.com/u/3753967/algorithms/Bcheck-0.6.tar.gz')
            local('tar -xzf Bcheck-0.6.tar.gz')
            local('rm Bcheck-0.6.tar.gz')
            local('ln -sf %s/Bcheck-0.6 ./Bcheck'%installation_directory)
            local('echo "export PATH=\$PATH:%s/Bcheck/" >> $HOME/.RnaSciToolbox'%installation_directory)

def blast(installation_directory = "%s/algorithms"%home):
    """
    Install Blast and NCBI-blast
    """
    print(green("Installing Blast..."))
    if not os.path.exists('%s/blast/bin'%installation_directory):
        local('echo "export PATH=\$PATH:%s/blast/bin" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/ncbi-blast/bin'%installation_directory):
        local('echo "export PATH=\$PATH:%s/ncbi-blast/bin" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/ncbi-blast-2.2.31+/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO blast-2.2.26-x64-linux.tar.gz http://dl.dropbox.com/u/3753967/algorithms/blast-2.2.26-x64-linux.tar.gz')
            local('tar -xzf blast-2.2.26-x64-linux.tar.gz')
            local('rm blast-2.2.26-x64-linux.tar.gz')
            local('ln -sf %s/blast-2.2.26 ./blast'%installation_directory)
            local('wget -qO ncbi-blast-2.2.31+-x64-linux.tar.gz https://dl.dropboxusercontent.com/u/3753967/algorithms/ncbi-blast-2.2.31+-x64-linux.tar.gz')
            local('tar -xzf ncbi-blast-2.2.31+-x64-linux.tar.gz')
            local('rm ncbi-blast-2.2.31+-x64-linux.tar.gz')
            local('ln -sf %s/ncbi-blast-2.2.31+ ./ncbi-blast'%installation_directory)

def blastR(installation_directory = "%s/algorithms"%home):
    """
    Install BlastR
    """
    print(green("Installing BlastR..."))
    if not os.path.exists('%s/blastR/scripts/'%installation_directory):
        local('echo "export PATH=\$PATH:%s/blastR/scripts/" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/blastR_package_V2.2/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO blastR_package_V2.2.tar.gz http://dl.dropboxusercontent.com/u/3753967/algorithms/blastR_package_V2.2.tar.gz')
            local('tar -xzf blastR_package_V2.2.tar.gz')
            local('rm blastR_package_V2.2.tar.gz')
            local('ln -sf %s/blastR_package_V2.2 ./blastR'%installation_directory)

def clustalw(installation_directory = "%s/algorithms"%home):
    """
    Install Clustalw
    """
    print(green("Installing ClustalW..."))
    if not os.path.exists('%s/clustalw/bin'%installation_directory):
        local('echo "export PATH=\$PATH:%s/clustalw/bin" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/clustalw_2.1/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO clustalw-2.1.tar.gz http://dl.dropbox.com/u/3753967/algorithms/clustalw-2.1.tar.gz')
            local('tar -xzf clustalw-2.1.tar.gz')
            local('rm clustalw-2.1.tar.gz')
            local('ln -sf %s/clustalw_2.1 ./clustalw'%installation_directory)
            with lcd('clustalw-2.1'):
                local('./configure --prefix=%s/clustalw_2.1'%installation_directory)
                local('make')
                local('make install')
            with lcd(installation_directory):
                local('rm -rf clustalw-2.1')

#problem to compile contrafold. For now, the dropbox provides a precompiled version for linux.
def contrafold(installation_directory = "%s/algorithms"%home):
    """
    Install Contrafold
    """
    print(green("Installing Contrafold..."))
    if not os.path.exists('%s/contrafold/src'%installation_directory):
        local('echo "export PATH=\$PATH:%s/contrafold/src" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/contrafold/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO contrafold.tar.gz http://dl.dropbox.com/u/3753967/algorithms/contrafold.tar.gz')
            local('tar -xzf contrafold.tar.gz')
            local('rm contrafold.tar.gz')

def gotohscan(installation_directory = "%s/algorithms"%home):
    """
    Install GotohScan
    """
    print(green("Installing GotohScan..."))
    if not os.path.exists('%s/GotohScan/src'%installation_directory):
        local('echo "export PATH=\$PATH:%s/GotohScan/src" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/GotohScan_2.0-alpha/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO GotohScan_2.0-alpha.tar.gz http://dl.dropbox.com/u/3753967/algorithms/GotohScan_2.0-alpha.tar.gz')
            local('tar -xzf GotohScan_2.0-alpha.tar.gz')
            local('rm GotohScan_2.0-alpha.tar.gz')
            local('ln -sf %s/GotohScan_2.0-alpha ./GotohScan'%installation_directory)
            with lcd('GotohScan'):
                local('make')

def infernal(installation_directory = "%s/algorithms"%home):
    """
    Install Infernal
    """
    print(green("Installing Infernal..."))
    if not os.path.exists('%s/infernal/bin'%installation_directory):
        local('echo "export PATH=\$PATH:%s/infernal/bin" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/infernal_1.0.2/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO infernal-1.0.2.tar.gz http://dl.dropbox.com/u/3753967/algorithms/infernal-1.0.2.tar.gz')
            local('tar -xzf infernal-1.0.2.tar.gz')
            local('rm infernal-1.0.2.tar.gz')
            local('ln -sf %s/infernal_1.0.2 ./infernal'%installation_directory)
            with lcd('infernal-1.0.2'):
                local('./configure --prefix="%s"/infernal_1.0.2'%installation_directory)
                local('make clean')
                local('make')
                local('make install')
            with lcd(installation_directory):
                local('rm -rf infernal-1.0.2')

def rnamotif(installation_directory = "%s/algorithms"%home):
    """
    Install RNAMotif
    """
    print(green("Installing RNAMotif..."))
    if not os.path.exists('%s/rnamotif/src'%installation_directory):
        local('echo "export PATH=\$PATH:%s/rnamotif/src" >> $HOME/.RnaSciToolbox'%installation_directory)
    if sys.platform != 'darwin': #if not OSX
        local("sudo apt-get -y install flex")
    if not os.path.exists('%s/rnamotif-3.0.7/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO rnamotif-3.0.7.tar.gz https://dl.dropboxusercontent.com/u/3753967/algorithms/rnamotif-3.0.7.tar.gz')
            local('tar -xzf rnamotif-3.0.7.tar.gz')
            local('rm rnamotif-3.0.7.tar.gz')
            local('ln -sf %s/rnamotif-3.0.7 ./rnamotif'%installation_directory)
            with lcd('rnamotif'):
                local('make')

def rnabob(installation_directory = "%s/algorithms"%home):
    """
    Install RNABOB
    """
    print(green("Installing RNABOB..."))
    if not os.path.exists('%s/rnabob/'%installation_directory):
        local('echo "export PATH=\$PATH:%s/rnabob/" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/rnabob-2.2.1/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO rnabob-2.2.1.tar.gz http://dl.dropbox.com/u/3753967/algorithms/rnabob.tar.gz')
            local('tar -xzf rnabob-2.2.1.tar.gz')
            local('rm rnabob-2.2.1.tar.gz')
            local('ln -sf %s/rnabob-2.2.1 ./rnabob'%installation_directory)
            with lcd('rnabob'):
                local('make')

def snogps(installation_directory = "%s/algorithms"%home):
    """
    Install SnoGPS
    """
    print(green("Installing SnoGPS..."))
    if not os.path.exists('%s/snoGPS/'%installation_directory):
        local('echo "export PATH=\$PATH:%s/snoGPS/" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/snoGPS/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO snoGPS-0.2.tar.gz https://dl.dropboxusercontent.com/u/3753967/algorithms/snoGPS-0.2.tar.gz')
            local('tar -xzf snoGPS-0.2.tar.gz')
            local('rm snoGPS-0.2.tar.gz')
            local('ln -sf %s/snoGPS-0.2 ./snoGPS'%installation_directory)
            with lcd('snoGPS/src'):
                local('make')

def snoreport(installation_directory = "%s/algorithms"%home):
    """
    Install snoReport
    """
    print(green("Installing snoReport..."))
    if not os.path.exists('%s/SnoReport/'%installation_directory):
        local('echo "export PATH=\$PATH:%s/SnoReport/" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/SnoReport1.0/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO SnoReport1.0.tgz http://dl.dropboxusercontent.com/u/3753967/algorithms/SnoReport1.0.tgz')
            local('tar -xzf SnoReport1.0.tgz')
            local('rm SnoReport1.0.tgz')
            local('ln -sf %s/SnoReport1.0 ./SnoReport'%installation_directory)
            with lcd('SnoReport'):
                #SnoReport needs the Vienna package in the PATH. How to do it?? TO DO!!!!!
                local('./install.sh')

def snoscan(installation_directory = "%s/algorithms"%home):
    """
    Install Snoscan
    """
    print(green("Installing Snoscan..."))
    if not os.path.exists('%s/snoscan/'%installation_directory):
        local('echo "export PATH=\$PATH:%s/snoscan/" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/snoscan-0.9b/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO snoscan-0.9b.tar.gz https://dl.dropboxusercontent.com/u/3753967/algorithms/snoscan.tar.gz')
            local('tar -xzf snoscan-0.9b.tar.gz')
            local('rm snoscan-0.9b.tar.gz')
            local('ln -sf %s/snoscan-0.9b ./snoscan'%installation_directory)
            with lcd('snoscan/squid-1.5j'):
                local('make')
            with lcd('snoscan/'):
                local('make')

def trnaScanSE(installation_directory = "%s/algorithms"%home):
    """
    Install tRNAscan-SE
    """
    print(green("Installing tRNAscan-SE..."))
    if not os.path.exists('%s/tRNAscan-SE/'%installation_directory):
        local('echo "export PATH=\$PATH:%s/tRNAscan-SE/bin" >> $HOME/.RnaSciToolbox'%installation_directory)
        local('echo "export PERL5LIB=%s/tRNAscan-SE/bin/:\$PERL5LIB" >> $HOME/.RnaSciToolbox'%installation_directory)
    if not os.path.exists('%s/tRNAscan-SE-1.3.1/'%installation_directory):
        with lcd(installation_directory):
            local('wget -qO tRNAscan-SE-1.3.1.tar https://dl.dropboxusercontent.com/u/3753967/algorithms/tRNAscan-SE-1.3.1.tar')
            local('tar -xf tRNAscan-SE-1.3.1.tar')
            local('rm tRNAscan-SE-1.3.1.tar')
            local('ln -sf %s/tRNAscan-SE-1.3.1 ./tRNAscan-SE'%installation_directory)
            with lcd('tRNAscan-SE'):
                #edition of the Makefile
                local('sed "s,\$(HOME),%s/tRNAscan-SE-1.3.1," Makefile > Makefile2'%installation_directory)
                local('mv Makefile2 Makefile')
                local('make')
                local('make install')
