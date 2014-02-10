sudo apt-get install python-pip
sudo apt-get install traceroute
sudo apt-get install nmap
sudo apt-get install python-nose
sudo apt-get install python-scapy
sudo apt-get install firefox
sudo apt-get install haskell-platform
sudo pip install paver
sudo pip install webdriverplus
sudo pip install fabric
sudo apt-get install libssl-dev libssl1.0.0
#scripts/install-threefish.sh
cabal install threefish
pushd ~
git clone https://github.com/blanu/Dust
cd Dust
git pull origin master
cd hs/Dust-crypto
cabal install
cd ..
cabal install
popd

pushd ~
git clone https://github.com/blanu/Dust-tools
cd Dust-tools
git pull origin master
cabal install
popd
