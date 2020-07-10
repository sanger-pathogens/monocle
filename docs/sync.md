# Sync

Below is a brief overview of Monocle's data sync process and the setup required on the OpenStack instance.

## Components
The main components of Monocle run on OpenStack, but the primary copies of the served data files live on the farm. Files can be shared between the farm and OpenStack by pushing to and then mounting a Ceph S3 bucket.

[![](https://mermaid.ink/img/eyJjb2RlIjoic2VxdWVuY2VEaWFncmFtXG4gICAgcGFydGljaXBhbnQgcGF0aHBpcGVAZmFybTVcbiAgICBwYXJ0aWNpcGFudCBTM1xuICAgIHBhcnRpY2lwYW50IHBhdGhwaXBlQGZjZV9pbnN0YW5jZVxuICAgIHBhcnRpY2lwYW50IGNvbnRhaW5lclxuICAgIE5vdGUgb3ZlciBwYXRocGlwZUBmYXJtNSwgUzM6IGNyb25cbiAgICBTMy0-PnBhdGhwaXBlQGZjZV9pbnN0YW5jZTogcmNsb25lIG1vdW50IC0tcmVhZC1vbmx5XG4gICAgcGF0aHBpcGVAZmNlX2luc3RhbmNlLT4-Y29udGFpbmVyOiB2b2x1bWUgbW91bnRcblx0cGF0aHBpcGVAZmFybTUtPj5TMzogcmNsb25lIHN5bmNcbiAgICBwYXRocGlwZUBmYXJtNS0-PlMzOiByY2xvbmUgc3luY1xuICAgIHBhdGhwaXBlQGZhcm01LT4-UzM6IHJjbG9uZSBzeW5jXG4gICAgTm90ZSBvdmVyIHBhdGhwaXBlQGZjZV9pbnN0YW5jZSwgY29udGFpbmVyOiBkZXBsb3kgbmV3IHJlbGVhc2VcbiAgICBwYXRocGlwZUBmY2VfaW5zdGFuY2UtPj5jb250YWluZXI6IHZvbHVtZSBtb3VudFxuXG5cdFx0XHRcdFx0IiwibWVybWFpZCI6eyJ0aGVtZSI6ImRlZmF1bHQifSwidXBkYXRlRWRpdG9yIjpmYWxzZX0)](https://mermaid-js.github.io/mermaid-live-editor/#/edit/eyJjb2RlIjoic2VxdWVuY2VEaWFncmFtXG4gICAgcGFydGljaXBhbnQgcGF0aHBpcGVAZmFybTVcbiAgICBwYXJ0aWNpcGFudCBTM1xuICAgIHBhcnRpY2lwYW50IHBhdGhwaXBlQGZjZV9pbnN0YW5jZVxuICAgIHBhcnRpY2lwYW50IGNvbnRhaW5lclxuICAgIE5vdGUgb3ZlciBwYXRocGlwZUBmYXJtNSwgUzM6IGNyb25cbiAgICBTMy0-PnBhdGhwaXBlQGZjZV9pbnN0YW5jZTogcmNsb25lIG1vdW50IC0tcmVhZC1vbmx5XG4gICAgcGF0aHBpcGVAZmNlX2luc3RhbmNlLT4-Y29udGFpbmVyOiB2b2x1bWUgbW91bnRcblx0cGF0aHBpcGVAZmFybTUtPj5TMzogcmNsb25lIHN5bmNcbiAgICBwYXRocGlwZUBmYXJtNS0-PlMzOiByY2xvbmUgc3luY1xuICAgIHBhdGhwaXBlQGZhcm01LT4-UzM6IHJjbG9uZSBzeW5jXG4gICAgTm90ZSBvdmVyIHBhdGhwaXBlQGZjZV9pbnN0YW5jZSwgY29udGFpbmVyOiBkZXBsb3kgbmV3IHJlbGVhc2VcbiAgICBwYXRocGlwZUBmY2VfaW5zdGFuY2UtPj5jb250YWluZXI6IHZvbHVtZSBtb3VudFxuXG5cdFx0XHRcdFx0IiwibWVybWFpZCI6eyJ0aGVtZSI6ImRlZmF1bHQifSwidXBkYXRlRWRpdG9yIjpmYWxzZX0)

## Setup on OpenStack instance

### Prerequisites
The following steps are needed on a fresh OpenStack instance. Ideally, they should be run automatically when provisioning in the future.
- install [rclone](https://rclone.org/)
- add `~/.config/rclone/rclone.conf` with identical content to on `pathpipe@farm5` (contains S3 secrets/keys, hence not in repo)
- ensure `/etc/fuse.conf` contains the line `user_allow_other` (which allows users other than the mounting user to access files on the instance; needed for Docker)

### Mount
Given a Ceph S3 origin (named `remote` from `rclone.conf`), mount the bucket `<bucket-name>` with:
```
rclone mount remote:<bucket-name> <local-dir> --read-only --allow-other --allow-root --vfs-cache-mode writes --daemon
```

### Unmount
Run:
```
fusermount -u <local-dir>
```
