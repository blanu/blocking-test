if [ ! -e "$HOME/.ssh/id_rsa.pub" ]; then
    echo "Generating SSH key"
    ssh-keygen
fi

if [ ! -e "/root/.ssh/id_rsa.pub" ]; then
  if [ -d "/root" ]; then
    echo "Copying user SSH key for root"
    cp ~/.ssh/id_rsa* /root/.ssh
    chown root /root/.ssh/id_rsa*
    chgrp root /root/.ssh/id_rsa*
  fi
fi

if [ ! -e "$HOME/.ssh/config" ]; then
    echo "Copying SSH config"
    cp ~/blocking-test/capture/config/ssh-config ~/.ssh/config
fi

scripts/install-deps.sh
