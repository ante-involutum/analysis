# analysis

数据服务，管理 [`plugin`](https://github.com/no8ge/plugins "plugin") 生成的测试日志、指标等数据

## 要求

- Kubernetes

## 快速开始

### 构建 plugin

> 参考 [`plugin`](https://github.com/no8ge/plugins "plugin")

### 部署环境

> 参考 [`快速开始`](https://github.com/no8ge/atop?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)

### 创建测试

> 参考 [`快速开始`](https://github.com/no8ge/tink?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)

#### 查看日志

```shell
# request
curl -X POST -H "Content-Type: application/json" -H "Authorization: admin" http://192.168.228.5:31690/analysis/v1.0/raw -d '
{
  "index":"logs",
  "key_words":
    {
      "kubernetes.pod.name":"278a0e0f-08a4-47b1-a4a8-582b21fcf694",
      "kubernetes.container.name": "pytest"

      },
    "from_":0,
    "size":200
}'

# response
{
    "total":14,
    "offset":[
        1702645117089,
        "RI-ObYwBNmgpk-7WziPr"
    ],
    "messages":[
        "============================= test session starts ==============================",
        "metadata: {'Python': '3.7.9', 'Platform': 'Linux-6.5.10-orbstack-00110-gbcfe04c86d2f-x86_64-with-debian-10.5', 'Packages': {'pytest': '7.2.0', 'pluggy': '1.0.0'}, 'Plugins': {'anyio': '3.6.2', 'html': '3.2.0', 'metadata': '3.0.0'}}",
        "platform linux -- Python 3.7.9, pytest-7.2.0, pluggy-1.0.0 -- /usr/local/bin/python",
        "cachedir: .pytest_cache",
        "rootdir: /demo",
        "plugins: anyio-3.6.2, html-3.2.0, metadata-3.0.0",
        "collecting ... collected 3 items",
        "",
        "tests/test_demo.py::TestDemo::test_read_root PASSED",
        "tests/test_demo.py::TestDemo::test_read_item PASSED",
        "------------- generated html file: file:///demo/report/report.html -------------",
        "tests/test_demo.py::TestDemo::test_anythings PASSED",
        "",
        "============================== 3 passed in 0.46s ==============================="
    ]
}
```
