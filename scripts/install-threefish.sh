pushd
cd
git clone https://github.com/blanu/threefish
cd threefish
git pull origin master
cabal install --force-reinstalls
popd
