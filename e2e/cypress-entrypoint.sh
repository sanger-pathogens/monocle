#!/usr/bin/env bash

echo "---------- cypress-entrypoint start ----------"

whoami
ls -l /root/.ssh
chown -R $UID:$UID /root/.ssh
apt install -y ssh-askpass
cypress run

echo "---------- cypress-entrypoint end ----------"