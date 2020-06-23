#!/usr/bin/env bash

echo "---------- cypress-entrypoint start ----------"

whoami
ls -l /root/.ssh
chown -R root:root /root/.ssh
cypress run

echo "---------- cypress-entrypoint end ----------"