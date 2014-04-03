if [ ! -e "/root/.ssh/id_rsa.pub" ]; then
  if [ -d "/root" ]; then
    echo "Copying user SSH key for root"
    cp ~/.ssh/id_rsa* /root/.ssh
    chown root /root/.ssh/id_rsa*
    chgrp root /root/.ssh/id_rsa*
  fi
fi
