# 百度搜索指数爬虫

获取给定关键字从 `2009-1-1` 到 `2017-12-31` 的百度搜索指数，以 `csv` 表格格式进行存储。

## 待查询数据

[`data/companies.txt`](data/companies.txt): 所有需要查询的公司名称，用 `，`（全角逗号） 分隔
`data/test.txt`: 测试用的关键字，用 `，` 分隔

## 查询结果

见 `results`。

## 处理流程

将 `config-sample.py` 重命名为 `config.py`，登录百度主页，打开 Chrome 开发者工具页面，复制 COOKIES，粘贴到 `config.py`。同时创建输出目录 `results`。

```bash
$ cp config-sample.py config.py 
$ mkdir results
$ make
```
> 注意：由于百度会对频繁访问进行限制，建议使用多个账户的 COOKIE 进行轮流切换使用。

1. 从 `companies.txt` 读取关键字，进行预处理
2. 加载配置信息，初始化 `BaiduIndex` 类
3. 对于每一个关键字，将查询区间分为诸多 180 天的小片段，循环进行查询
   1. 使用 `get_encrypt_datas` 得到 `encrypt_data` 和 `uniqid`
   2. 使用 `uniqid` 得到 `key`，再用 `key` 对 `encrypt_data` 进行解密得到其中包含的有价值信息
4. 一个查询完毕后，更新 `.csv` 表格文档

## 错误处理

经过不断调试，发现大致有三种错误。在发生错误时程序会对用户进行提示，建议处理方法如下：

1. 未收录：跳过
2. 访问过于频繁：稍等一会儿之后，再重新尝试，或者切换另一个账户的 COOKIE
3. Connection reset by peer / 其他少见错误：立即重试

> 对于访问过于频繁的错误，建议选择切换 COOKIE 进行尝试。

在运行出错时，用户根据命令行提示进行选择即可。

### 未收录

https://index.baidu.com/v2/main/index.html#/trend/%E4%B8%AD%E8%88%AA%E5%96%84%E8%BE%BE?words=%E4%B8%AD%E8%88%AA%E5%96%84%E8%BE%BE

![20190221124836.png](https://i.loli.net/2019/02/21/5c6e2da60281c.png)

![20190221140223.png](https://i.loli.net/2019/02/21/5c6e3ef076ee2.png)

### Connection reset by peer

![20190221151506.png](https://i.loli.net/2019/02/21/5c6e4ffb9285f.png)

### 访问过于频繁

报错如下：

```txt
错误:  string indices must be integers
```

究其根源：

![20190221132527.png](https://i.loli.net/2019/02/21/5c6e36493943e.png)

![20190221140158.png](https://i.loli.net/2019/02/21/5c6e3ed79e82f.png)

## 致谢

1. https://github.com/wangbingyan90/python_project (The basis of this project)
2. https://github.com/longxiaofei/spider-BaiduIndex (Area codes, test usage)