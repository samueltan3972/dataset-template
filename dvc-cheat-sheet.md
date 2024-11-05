# DVC Cheat Sheet

## Setup

* [DVC Install](https://dvc.org/doc/install)

```bash
dvc init
pip install dvc[ssh]
dvc remote add remote_name ssh://default_user@127.0.0.1/default
dvc remote modify remote_name user default_user
dvc remote modify remote_name password default_password
dvc remote default remote_name
```

## Pushing to remote

```bash
dvc add abc.csv
git add *.dvc
git commit -m "Add dvc"
git push
dvc push
```

## Pulling from remote

```bash
dvc pull
dvc get
```

 
## Misc

Ways to connect remote storage - as defined in the dvc config file (.dvc\config)

1. WebDAV (Windows & Linux)

```yml
['remote "default"']
    url = webdav://127.0.0.1:5005/
    user = default_user
    password = default_password@12345
```

2. SSH - (Windows & Linux)

```yml
['remote "default"']
    url = ssh://default_user@127.0.0.1
    user = default_user
    password = default_password
```

3. Linux pointer to mounted directory

```yml
['remote "default"']
    url = /home/user/dataset-template
```

4. Windows pointer to mounted directory

```yml
['remote "default"']
    url = Z:/dvc
```
