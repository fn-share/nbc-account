nbc-account
----------------

A tool for NBC account management.

&nbsp;

## 关于 nbc-account 工具

本工具用于创建适用于 NBC 系统的账号，同时在用的账号可以有一个，或者多个。这些账号在 `config.json` 配置文件中保存，并且，选中一个账号用于表达 “当前在用账号”，也就是 `config.json` 文件中由 `default` 配置项指明的那个账号。

本工具为一组 NBC 账号提供如下操作：

1. 创建新账号，可选设置保护密码
2. 移除指定账号
3. 列出现有账号
4. 切换当前账号，即，修改 `default` 配置指向
5. 将指定账号导出，以便在其它机器中导入使用
6. 导入账号

本项目重用了 [ricmoo/pycoind](https://github.com/ricmoo/pycoind) 项目中 util 模块的代码，`ricmoo/pycoind` 以 MIT 许可证开源，对本项目我们继续采用 MIT 许可证开源。

&nbsp;

## 命令行用法

运行 `python3 account.py --help` 将打印如下信息：

``` bash
Usage: account.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  delete
  export
  generate
  import
  list
  setdefault
```

用户可以进一步查取帮助，如 `python3 account.py generate --help`，`python3 account.py export --help` 等。

本项目主要用于展示在本地如何用 NBC 账号构造 HD 钱包支持，它支持的命令行操作大致分两类，其一是查询信息，其二是修改账号信息，带来若干变动将存入 `data/config.json` 文件。

&nbsp;

## 关于 NBC 账号

NBC 账号主体格式顺从比特币数字钱包的制式，改动很少。

主要改进是增加了虚拟链号（Virtual Chain Number，vcn）指定，vcn 取值范围为 `0 ~ 65535`，适合用于描述 NBC 并行链中数字钱包的账号。vcn 取值对应于并行链的链号，我们将 vcn 取值融入到钱包地址格式中，便于转账发起后，系统能自动定位相关账号归属于哪条并行链，由相应并行链负责向外付款（即，兑付 UTXO）。

本项目还展示了 vcn 用 `None` 值创建的账号，等效于 BTC 的账号格式，格式未变，而只有 vcn 取 `0~65535` 时创建的账号，才适用于 NBC 并行链，额外记录 vcn 信息。

&nbsp;
