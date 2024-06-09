<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://source.cclmsy.cc/Images/nbp_Sparkapi/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://source.cclmsy.cc/Images/nbp_Sparkapi/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
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

基于Nonebot2平台，科大讯飞星火大语言模型官方API的AI聊天机器人插件

适用于所有模型版本（默认当前最新（v3.5）），支持上人物预设、AI绘图、AI生成PPT等功能

### 💬 功能
- [x] 支持AI对话
- [x] 支持上下文关联记忆（可设置记忆文本长度）
- [x] 用户鉴别（每个用户的历史记录独立）
- [x] 支持用户自定义、更改、切换预设（Prompt）
- [x] 自动生成人物预设菜单、帮助列表，无需重写
- [x] 基于pickle的历史记录持久化
- [x] 完善的配置项（有其他需求请发issue）
- [x] 支持AI绘图（AI Image Generation）
- [x] 支持AI生成PPT（PPT Generation）
- [ ] 用户权限与功能区分（超级用户、普通用户）
- [ ] 用户画像（记录用户信息以便提供更精确的内容）（目前存争议，考虑允许用户自行设置）

### 📦 项目地址
- Github：https://github.com/CCLMSY/nonebot-plugin-sparkapi 
- Pypi：https://pypi.org/project/nonebot-plugin-sparkapi/
- Nonebot：https://registry.nonebot.dev/plugin/nonebot-plugin-sparkapi:nonebot_plugin_sparkapi
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

AI绘图、AI生成PPT功能的API信息一般与对话API信息相同（同一应用），但是开启相应功能前需要在讯飞开放平台申请相应的服务

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| SPARKAPI_APP_ID | 是 | "" | APPID |
| SPARKAPI_API_SECRET | 是 | "" | APISecret |
| SPARKAPI_API_KEY | 是 | "" | APIKey |
| SPARKAPI_MODEL_VERSION | 否 | "" | 星火大模型的版本，默认为当前最新。<br>可选值：v3.5, v3.0, v2.0, v1.5 |
| SPARKAPI_MODEL_TOP_K | 否 | 4 | 平衡生成文本的质量和多样性。<br>较小的 k 值会减少随机性，使得输出更加稳定；<br>而较大的 k 值会增加随机性，产生更多新颖的输出。<br>取值范围[1, 6] |
| SPARKAPI_MODEL_TEMPERATURE | 否 | 0.5 | 控制结果随机性，取值越高随机性越强，即相同的问题得到的不同答案的可能性越高。<br>取值范围 (0，1] |
| SPARKAPI_MODEL_MAXKLENGTH | 否 | 8000 | 上下文最大长度，[1,8000]<br>单次发送和回复的消息不能超过该项的一半 |
| SPARKAPI_PRIORITY | 否 | 80 | 该值越小，事件越先被触发。本插件建议设置较大的值。可选值：1~97<br>若触发本插件事件，所有插件中优先级大于此值的事件都将被阻断。<br>本插件中事件的优先级顺序：私聊阻断（=priority）< 功能（=priority+1）< 对话（=priority+2） |
| SPARKAPI_COMMAND_CHAT | 否 | "" | 机器人对话指令，默认为空可直接对话<br>（需要同时在`.env`中配置命令起始字符为空：COMMAND_START = [""]） |
| SPARKAPI_FL_NOTICE | 否 | True | 收到请求时是否提示“已收到请求” |
| SPARKAPI_FL_SETPRESET_CLEAR | 否 | True | 切换人物预设时是否清除当前对话上下文 |
| SPARKAPI_FL_PRIVATE_CHAT | 否 | True | 是否允许私聊使用 |
| SPARKAPI_FL_GROUP_PUBLIC | 否 | False | 群聊启用公共会话<br>True：所有人共享同一会话<br>False：每个人的会话各自独立 |
| SPARKAPI_FL_GROUP_AT | 否 | True | 群聊回复消息时是否需要@提问者 |
| SPARKAPI_FL_IMGGEN | 否 | False | 是否启用AI绘图功能 |
| SPARKAPI_FL_PPTGEN | 否 | False | 是否启用AI生成PPT功能 |
| SPARKAPI_BOT_NAME | 否 | "" | 机器人的名字 |

以下配置项请查看`/.venv/Lib/nonebot_plugin_sparkapi/config.py`修改：
1. sparkapi_commands：指令表（允许单个字符串或字符串列表）
2. sparkapi_commands_info：指令表说明（用于生成帮助信息）
3. sparkapi_message_blockprivate：阻断私聊时的提示信息

## 🎉 使用
### 指令表（默认）
以下所有指令均可在config.py中修改，且无需重写菜单/指令生成函数

| 指令 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|
| SPARKAPI_COMMAND_CHAT（若不为空） + 对话内容 | 是 | 私聊/群聊 | 与机器人进行对话 |
| help/帮助 | 是 | 私聊/群聊 | 显示帮助信息 |
| preset/人物预设 | 是 | 私聊/群聊 | 显示人物预设菜单和当前预设 |
| set/切换预设 | 是 | 私聊/群聊 | 显示人物预设菜单，选择人物预设并切换 |
| set/切换预设 + 人物名 | 是 | 私聊/群聊 | 切换人物预设 |
| create/创建预设 | 是 | 私聊/群聊 | 创建自定义的人物预设 |
| delete/删除预设 | 是 | 私聊/群聊 | 删除自定义的人物预设 |
| delete/删除预设 + 人物名 | 是 | 私聊/群聊 | 显示自定义人物预设菜单, 选择人物预设并删除 |
| clear/清空对话 | 是 | 私聊/群聊 | 清除当前对话上下文 |
| save/保存对话 | 是 | 私聊/群聊 | 保存当前对话记录 |
| load/加载对话 | 是 | 私聊/群聊 | 加载上次保存的对话记录 |
| imggen/AI绘图 + 描述 | 是 | 私聊/群聊 | AI根据描述生成图片 |
| imggen/AI绘图 | 是 | 私聊/群聊 | 下一句给出描述，AI根据描述生成图片 |
| pptgen/AIPPT + 描述 | 是 | 私聊/群聊 | AI根据描述生成PPT |
| pptgen/AIPPT | 是 | 私聊/群聊 | 下一句给出描述，AI根据描述生成PPT |

### 人物预设
1. 智能助手（默认）
2. 心理咨询师
3. 李白

### 效果图
![demo](https://source.cclmsy.cc/Images/nbp_Sparkapi/demo.jpg)
