# Secret keys
In production, Django needs a `SECRET_KEY` setting, which should not be stored in version control.

At present, this is loaded on deployment from a file `/home/pathpipe/.ssh/environment` on the OpenStack VM, which has the following format:
```
API_SECRET_KEY=<some-string-of-50-random-alphanumeric-characters>
```

## Allowing ssh remote environments
To enable one or more remote environment variables (from `~/.ssh/environment`) to be loaded when `ssh`ing into the OpenStack VM, add the following line to `etc/ssh/sshd_config` if not present:
```
PermitUserEnvironment yes
```

Restart the service:
```
sudo service sshd restart
```
