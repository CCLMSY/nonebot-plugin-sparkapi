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
- [x] 支持AI对话
- [x] 支持上下文关联记忆（可设置记忆文本长度）
- [x] 用户鉴别（每个用户的历史记录独立）
- [x] 支持使用、切换人物预设（prompt）
- [x] 人物预设菜单自动生成，更改无需重写
- [x] 功能菜单自动生成，更改无需重写
- [x] 完善的配置项（有其他需求请发issue）
- [x] 历史记录持久化
- [ ] 实用功能列表（查天气、查快递等）
- [ ] 用户权限与功能区分（超级用户、普通用户）
- [ ] 支持星火助手API
- [ ] 支持用户自定义、更改预设

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
| SPARKAPI_APP_ID | 是 | "" | APPID |
| SPARKAPI_API_SECRET | 是 | "" | APISecret |
| SPARKAPI_API_KEY | 是 | "" | APIKey |
| SPARKAPI_MODEL_VERSION | 否 | "" | 星火大模型的版本，默认为当前最新。<br>可选值：v3.5, v3.0, v2.0, v1.5 |
| SPARKAPI_MODEL_TOP_K | 否 | 4 | 平衡生成文本的质量和多样性。<br>较小的 k 值会减少随机性，使得输出更加稳定；<br>而较大的 k 值会增加随机性，产生更多新颖的输出。<br>取值范围[1, 6] |
| SPARKAPI_MODEL_TEMPERATURE | 否 | 0.5 | 控制结果随机性，取值越高随机性越强，即相同的问题得到的不同答案的可能性越高。<br>取值范围 (0，1] |
| SPARKAPI_COMMAND_CHAT | 否 | "" | 机器人对话指令，默认为空可直接对话<br>（需要同时在`.env`中配置命令起始字符为空<br>COMMAND_START = [""]） |
| SPARKAPI_PRIVATE_CHAT | 否 | True | 是否允许私聊使用 |
| SPARKAPI_GROUP_PUBLIC | 否 | False | 群聊启用公共会话<br>True：所有人共享同一会话<br>False：每个人的会话各自独立 |
| SPARKAPI_GROUP_AT | 否 | True | 群聊回复消息时是否需要@提问者 |
| SPARKAPI_FNOTICE | 否 | True | 收到请求时是否提示“已收到请求” |
| SPARKAPI_PRIORITY | 否 | 90 | 事件响应器优先级，[1,99]，数字越小优先级越高 |
| SPARKPAI_MAX_LENGTH | 否 | 8000 | 上下文最大长度，[1,8000]<br>单次发送和回复的消息不能超过该项的一半 |
| SPARKAPI_SETPRESET_CLEAR | 否 | True | 切换人物预设时是否清除当前对话上下文 |
| SPARKAPI_BOT_NAME | 否 | "" | 机器人的名字 |


## 🎉 使用
### 指令表
所有指令均可在data.py中修改，且无需重写菜单/指令生成函数

| 指令 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|
| sparkapi_command_chat（若不为空） + 对话内容 | 是 | 私聊/群聊 | 与机器人进行对话 |
| help | 是 | 私聊/群聊 | 查看帮助信息 |
| showpresets | 是 | 私聊/群聊 | 查看当前可选的人物预设 |
| setpreset | 是 | 私聊/群聊 | 查看当前可选的人物预设<br>回复编号以进行切换<br> |
| setpreset + 人物预设编号 | 是 | 私聊/群聊 | 切换到编号对应的人物预设 |
| savesession | 是 | 私聊/群聊 | 保存当前对话上下文 |
| loadsession | 是 | 私聊/群聊 | 加载之前保存的对话上下文 |
| clear | 是 | 私聊/群聊 | 清除当前对话上下文 |

### 效果图
![demo](https://github.com/CCLMSY/nonebot-plugin-sparkapi/blob/resources/demo.jpg)
