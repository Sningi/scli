# scli

### 1. install by setup tools
1.1 install for bash/zsh
```shell
pip3 install --editable .
```
### 2. add bash/zsh tab autocompletion
2.1 add line to ~/.bashrc 

```shell
eval "$(_SCLI_COMPLETE=source scli)"
eval "$(_SCLI_COMPLETE=source_zsh scli)"
#click 8
eval "$(_SCLI_COMPLETE=bash_source scli)"
```
2.2 effective
```shell
source ~/.bashrc
```
### 3. Usage
```
scli sctp-stat show
scli sctp-cfg enable nas_decrypt
```

### 4. config 
```
vim scli.cfg
```

### 5. test

```
pytest -v test.py
```
