if [ ! -e "$HOME/.ssh/id_rsa.pub" ]; then
    echo "Generating SSH key"
    expect -c "
      spawn ssh-keygen -b 2048 -t rsa -f "$HOME/.ssh/id_rsa" -q
      expect \"Enter passphrase (empty for no passphrase):\"
      send \"\r\"
      expect \"Enter same passphrase again:\"
      send \"\r\"
    "
fi

if [ ! -e "$HOME/.ssh/config" ]; then
    echo "Copying SSH config"
    cp ~/blocking-test/capture/config/ssh-config ~/.ssh/config
fi

sudo scripts/check-root-sshkeys.sh

scripts/install-deps.sh
