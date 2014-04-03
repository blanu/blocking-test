if [ ! -e "$HOME/.ssh/id_rsa.pub" ]; then
    echo "Generating SSH key"
    ssh-keygen
fi

if [ ! -e "$HOME/.ssh/config" ]; then
    echo "Copying SSH config"
    cp ~/blocking-test/capture/config/ssh-config ~/.ssh/config
fi

sudo scripts/check-root-sshkeys.sh

scripts/install-deps.sh
