cd ~/blocking-test/capture
echo "Launching tests"
#../scripts/progressbar.sh
echo "Please enter your root password when prompted."
sudo paver -q all
#killall progressbar.sh
echo "Tests complete."
