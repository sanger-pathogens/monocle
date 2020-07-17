# Secret keys
In production, Django needs a `SECRET_KEY` setting, which should not be stored in version control.

At present, this is loaded on deployment from a file `/home/pathpipe/.monocle-secrets` on the OpenStack VM, which has the following format:
```
export SECRET_KEY="<some-string-of-50-random-characters>"
```

To generate a new string, you could use eg. `base64 /dev/urandom | head -c50`.