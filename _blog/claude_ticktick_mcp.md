# 在 Claude Code 中使用 MCP 扩展功能

## Claude Code 里面安装 TickTick MCP

一个是 Claude Code 的 MCP 接入文档：[通过 MCP 将 Claude Code 连接到工具](https://code.claude.com/docs/zh-CN/mcp)，另一个是 [TickTick MCP](https://help.ticktick.com/articles/7438129581631995904) 官方的提供的 MCP 的文档。

直接添加上，然后重启 Claude Code。

```shell
claude mcp add -transport http ticktick https://mcp.ticktick.com
```

触发一下 Auth，然后就可以直接创建任务了。

简单的比如创建任务、创建带时间的任务、往某个项目里创建任务（会先 list 一下项目拿到项目 id，然后再往里面添加）…

## 扩展一下，自己创建 MCP

有时候一些固定的工作可以写成脚本，然后再生成一个本地的 MCP 包裹起来，就可以方便地用 AI 来触发它。整个过程都可以让 Claude Code 来完成。
