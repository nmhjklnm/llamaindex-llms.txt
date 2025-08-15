# CLI#
`llamactl` is a command line interface that ships with LlamaDeploy and has the main goal to easily interact with a running API Server.
# llamactl#
**Usage:**
```
llamactl [OPTIONS] COMMAND [ARGS]...

```

**Options:**
```
  --version            Show the version and exit.
  -s, --server TEXT    Apiserver URL
  -k, --insecure       Disable SSL certificate verification
  -t, --timeout FLOAT  Timeout on apiserver HTTP requests
  --help               Show this message and exit.

```

## llamactl deploy#
**Usage:**
```
llamactl deploy [OPTIONS] DEPLOYMENT_CONFIG_FILE

```

**Options:**
```
  --reload
  --help    Show this message and exit.

```

## llamactl run#
**Usage:**
```
llamactl run [OPTIONS]

```

**Options:**
```
  -d, --deployment TEXT     Deployment name  [required]
  -a, --arg <TEXT TEXT>...  'key value' argument to pass to the task, e.g. '-a
                            age 30'
  -s, --service TEXT        Service name
  -i, --session-id TEXT     Session ID
  --help                    Show this message and exit.

```

## llamactl sessions#
**Usage:**
```
llamactl sessions [OPTIONS] COMMAND [ARGS]...

```

**Options:**
```
  --help  Show this message and exit.

```

### llamactl sessions create#
**Usage:**
```
llamactl sessions create [OPTIONS]

```

**Options:**
```
  -d, --deployment TEXT  Deployment name  [required]
  --help                 Show this message and exit.

```

## llamactl status#
**Usage:**
```
llamactl status [OPTIONS]

```

**Options:**
```
  --help  Show this message and exit.

```

