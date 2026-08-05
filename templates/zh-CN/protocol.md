# Ho CodeFlow 协议 v1

各阶段共用的规则。`scripts/init_project.py` 会把这份文件复制进项目，成为
`.ho/protocol.md`，代理在运行时读的就是那一份。

> 字段名、状态值和文件名保持英文；正文用中文。

## 目录结构

```
<project>/
├── .ho/
│   ├── config.yaml
│   ├── protocol.md
│   └── changes/
│       └── 2026-08-05-example-change/
│           ├── change.yaml
│           ├── 01-design.md
│           ├── 02-implementation.md
│           └── 03-review.md
└── <项目文件>
```

变更 id 是 `YYYY-MM-DD-<slug>`，目录名与之同名。

## 状态

`change.yaml` 是状态唯一存放处。不要在 markdown 产物里再记一份状态——同一个状态有
两份副本，迟早会互相矛盾。

`status` 取值为 `draft`、`ready_for_implementation`、`implementing`、
`ready_for_review`、`rework`、`complete`、`abandoned` 之一。没有 `blocked`：
因为一个问题而停下的工作，保持它停下时所处阶段的状态，问题写在产物里。

```
draft                    -> ready_for_implementation
ready_for_implementation -> implementing
implementing             -> ready_for_review
ready_for_review         -> complete
ready_for_review         -> rework
rework                   -> implementing        （round += 1）
任何未完成状态            -> abandoned           （仅在用户明确要求时）
```

`ready_for_implementation` 记录的是用户的批准，不是设计者「我写完了」的感觉。只要
`01-design.md` 的 `Open questions` 下还有内容，就停在 `draft`；那里什么都没有时，同样
停在 `draft`——没有问题可问，不等于已经被批准。推进它的是用户，或者是 `ho-flow`（当
用户要求了 `auto`，那就是预先给出的批准）。

存在待答问题时，用户的回答同时就是批准。他们不需要说两次「可以」。

`review_kind` 是 `self` 或 `independent`，由写验收报告的人根据自己是否也做了设计或
实现来填。

每个阶段填自己那一栏角色——`designer`、`implementer`、`reviewer`——并在落盘时刷新
`updated_at`。角色只是给读历史的人看的自由文本标签，没有任何逻辑依赖它的拼写。

## 选哪个变更

同时有多个变更处于打开状态、而请求没有点名其中任何一个时，列出候选并询问。不要根据
时间新旧、排列顺序、或哪个看起来更完备去推断，也不要全都做。

## 哪些操作必须停下等批准

无论收到什么「一路做完」的指示：

- 不可逆删除
- 数据迁移
- 写入本项目之外的系统
- 发布或发送任何别人会看到的内容
- 生产环境变更
- 本项目自己的规则所管辖的任何操作

核对影响范围与请求一致，确认的是「会发生什么」。它并不确认「你可以这么做」。

## 证据

代码事实来自文件本身，不来自上一阶段对文件的转述。测试结论来自本轮运行的命令。无法
核实的条目记为 `unverified` 并写明原因；带着 `unverified` 项能否算 `complete`，由设计
中的完成定义决定。

Ho CodeFlow 不规定引用格式。沿用项目已有的做法。

## 并行修改

首次读取你打算改动的文件时，记录其 SHA-256。落盘前重新读取并比对。若它变了且不是你
改的，把你的改动叠加到新内容上；两者语义冲突时询问。绝不用回退、整文件覆盖或恢复旧
副本来处理一次来源不明的改动。

## 优先级

项目自己的说明文件——`AGENTS.md`，或你的宿主读取的任何等价文件——优先于本协议。
平台与安全规则优先于这里的一切。

## 语言

产物正文跟随用户语言。字段名、状态值和文件名在任何语言下都保持此处所写的英文形式。
