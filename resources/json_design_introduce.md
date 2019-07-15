使用json作为问答对的设置，说一下啊设计格式

```javascript
{
    "qa":[
        {
            "pattern":匹配的模式,
            "mode": 匹配的方式 有 equal|in|re三种，默认是equal,
            "ans":["abc"] //答案列表，多个答案选一种
        }
        ....
    ] //所有问答对
    "standard": [
    {
      "pattern": ".{0,5}天气.{0,5}", //搜索引擎的问法可能会导致解析的结果不一致，替换成标砖问答
        "mode": 匹配的方式 有 equal|in|re三种，默认是equal,
      "standard":"最近天气怎么样"，
      "replace":{ //可以在src内的全部字符串替换成target,该字段默认为None，当不为None时，无效化standard字段
        "src":["多少号","几多号","什么日子"],
        "target":"时间"
      },
    }
}
```

