#!/usr/bin/env bash

echo "---------- cypress-entrypoint start ----------"

whoami
ls -l /root/.ssh
chown -R $UID:$UID /root/.ssh
ls -l /root/.ssh
cypress run

echo "---------- cypress-entrypoint end ----------"