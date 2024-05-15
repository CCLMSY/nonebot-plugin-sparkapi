<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-sparkapi

_✨ 科大讯飞星火大语言模型官方API聊天机器人 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/CCLMSY/nonebot-plugin-sparkapi.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-sparkapi">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-sparkapi.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

基于Nonebot2平台，调用科大讯飞星火大语言模型官方API的AI聊天机器人插件

适用于所有模型版本（默认当前最新（v3.5）），支持上下文关联、人物预设等功能

### 💬 功能
- [x] 支持对话
- [x] 支持上下文关联记忆（可设置记忆文本长度）
- [x] 用户鉴别（每个用户的历史记录独立）
- [x] 支持使用、切换人物预设（prompt）
- [x] 更改人物预设无需重写菜单
- [x] 完善的配置项（有其他需求请发issue）
- [ ] 用户权限区分（超级用户、普通用户）
- [ ] 用户自定义预设
- [ ] 基于pickle的历史记录持久化

### 📦 项目地址
- Github：https://github.com/CCLMSY/nonebot-plugin-sparkapi 
- 觉得好用的话，请给个 Star⭐️ 谢谢喵~ 

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-sparkapi

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-sparkapi
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-sparkapi
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-sparkapi
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-sparkapi
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_sparkapi"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

其中，服务接口认证信息 app_id, api_secret, api_key 请前往 [讯飞开放平台控制台](https://console.xfyun.cn/) 获取

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| sparkapi_app_id | 是 | "" | APPID |
| sparkapi_api_secret | 是 | "" | APISecret |
| sparkapi_api_key | 是 | "" | APIKey |
| sparkapi_model_version | 否 | "" | 星火大模型的版本，默认为当前最新。<br>可选值：v3.5, v3.0, v2.0, v1.5 |
| sparkapi_command | 否 | "" | 机器人对话指令，默认为空可直接对话<br>（需要同时在`.env`中配置命令起始字符为空<br>COMMAND_START = [""]） |
| sparkapi_private_chat | 否 | True | 是否允许私聊使用 |
| sparkapi_group_public | 否 | False | 群聊启用公共会话<br>True：所有人共享同一会话<br>False：每个人的会话各自独立 |
| sparkapi_group_at | 否 | True | 群聊回复消息时是否需要@提问者 |
| sparkapi_fnotice | True | 否 | 收到请求时是否提示“已收到请求” |
| sparkapi_priority | 否 | 90 | 事件响应器优先级，[1,99]，数字越小优先级越高 |
| sparkpai_max_length | 否 | 8000 | 上下文最大长度，[1,8000]<br>单次发送的消息不能超过该项的一半 |
| sparkapi_bot_name | 否 | "" | 机器人的名字 |


## 🎉 使用
### 指令表
| 指令 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|
| sparkapi_command（若不为空） + 对话内容 | 是 | 私聊/群聊 | 与机器人进行对话 |
| help | 是 | 私聊/群聊 | 查看帮助信息 |
| showpresets | 是 | 私聊/群聊 | 查看当前可选的人物预设 |
| setpreset | 是 | 私聊/群聊 | 查看当前可选的人物预设<br>回复编号以进行切换<br> |
| setpreset + 人物预设编号 | 是 | 私聊/群聊 | 切换到编号对应的人物预设 |
| clear | 是 | 私聊/群聊 | 清除当前对话上下文 |

### 效果图
![demo1](https://github.com/CCLMSY/nonebot-plugin-sparkapi/blob/resources/demo1.jpg)
