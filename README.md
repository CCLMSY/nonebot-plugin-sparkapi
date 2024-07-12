<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://source.cclmsy.cc/Images/nbp_Sparkapi/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://source.cclmsy.cc/Images/nbp_Sparkapi/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-sparkapi

_✨ 科大讯飞星火大模型官方API聊天机器人 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/CCLMSY/nonebot-plugin-sparkapi.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-sparkapi">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-sparkapi.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

基于Nonebot2平台/科大讯飞星火大模型官方API的AI聊天机器人插件，适配OneBotV11协议

适用于所有模型版本（默认当前最新（v4.0）），同时支持自定义人物预设、会话管理，兼具AI绘图、AI生成PPT等功能

开发环境：Python3.11.8 on Conda, Windows 11

### 📦 项目地址
- Github：https://github.com/CCLMSY/nonebot-plugin-sparkapi 
- Pypi：https://pypi.org/project/nonebot-plugin-sparkapi/
- NoneBot：https://registry.nonebot.dev/plugin/nonebot-plugin-sparkapi:nonebot_plugin_sparkapi
- 作者主页：https://cclmsy.cc
- 觉得好用的话，请给个 Star⭐️ 谢谢喵~ 

### 💬 功能
- [x] 支持AI对话（已适配星火4.0API）
- [x] 支持上下文关联
- [x] 支持自定义预设、预设管理
- [x] 支持会话存储和加载、会话管理
- [x] 支持预设和历史记录持久化（基于json）
- [x] 完善配置项（有其他需求请发issue）
- [x] 支持AI绘图（Image Generation）
- [x] 支持AI生成PPT（PPT Generation）
- [ ] 用户权限与功能区分（超级用户、普通用户）
- [ ] 用户画像（记录用户信息以便提供更精确的内容，目前存争议，考虑允许用户自行设置）

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

## ⚙️ 配置项
在 nonebot2 项目的`.env`文件中添加下列配置项中的必填配置（SPARKAPI_APP_ID, SPARKAPI_API_SECRET, SPARKAPI_API_KEY）

服务接口认证信息 app_id, api_secret, api_key 请前往 [讯飞开放平台控制台](https://console.xfyun.cn/) 获取

AI绘图、AI生成PPT功能的API信息在同一应用下与对话API信息相同，开启相应功能前需要在讯飞开放平台申请相应的服务用量

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| SPARKAPI_APP_ID | 是 | "" | APPID |
| SPARKAPI_API_SECRET | 是 | "" | APISecret |
| SPARKAPI_API_KEY | 是 | "" | APIKey |
| SPARKAPI_MODEL_VERSION | 否 | "" | 星火大模型的版本，默认为当前最新。<br>可选值："default", "v4.0", "v3.5", "v3.0", "v2.0", "v1.5" |
| SPARKAPI_MODEL_TOP_K | 否 | 4 | 平衡生成文本的质量和多样性。<br>较小的 k 值会减少随机性，使得输出更加稳定；<br>而较大的 k 值会增加随机性，产生更多新颖的输出。<br>取值范围[1, 6] |
| SPARKAPI_MODEL_TEMPERATURE | 否 | 0.5 | 控制结果随机性，取值越高随机性越强，即相同的问题得到的不同答案的可能性越高。<br>取值范围 (0，1] |
| SPARKAPI_MODEL_MAXKLENGTH | 否 | 8000 | 单次上下文最大token长度，建议取值范围：[4000,8000]。<br>详细说明见下文 |
| SPARKAPI_PRIORITY | 否 | 80 | 本插件响应事件的优先级，建议设置较大的值。可选值：1~97。<br>详细说明见下文 |
| SPARKAPI_COMMAND_CHAT | 否 | "" | 机器人对话指令，默认为""可直接对话|
| SPARKAPI_FL_NOTICE | 否 | True | 收到对话请求时是否提示“已收到请求” |
| SPARKAPI_FL_PRIVATE_CHAT | 否 | True | 是否允许私聊使用 |
| SPARKAPI_FL_GROUP_PUBLIC | 否 | False | 群聊启用公共会话<br>True：所有人共享同一会话<br>False：每个人的会话各自独立 |
| SPARKAPI_FL_INTERFLOW | 否 | FALSE |  对于同一用户，群聊与私聊数据互通（公共会话启用时，群聊仍独立） |
| SPARKAPI_FL_GROUP_AT | 否 | True | 群聊回复消息时是否需要@提问者 |
| SPARKAPI_FL_IMGGEN | 否 | False | 是否启用AI绘图功能 |
| SPARKAPI_FL_PPTGEN | 否 | False | 是否启用AI生成PPT功能 |
| SPARKAPI_IG_SIZE | 否 | [1280,720] | AI绘图的图片尺寸，[宽,高]。<br>可选值和API消耗见下文 |
| SPARKAPI_BOT_NAME | 否 | "" | 机器人的名字 |

### SPARKAPI_MODEL_MAXKLENGTH
- 单次上下文最大token长度，不能超过8000token。建议取值范围：[4000,8000]
- 该值越大，对话历史记录保留越长，单次请求消耗token的最大值越大。
- 1token≈1.5个中文字≈1个英文单词。保守起见，在本插件中1token取1.25个字符
- QQ单条消息上限4500个字符（计3600token），消息超过最大长度可能导致响应不正确

### SPARKAPI_PRIORITY
- 响应事件的优先级，该值越小，事件越先被本插件响应。可选值：1~97
- 本插件中事件的优先级顺序：私聊阻断（=priority）< 功能（=priority+1）< 对话（=priority+2）
- 若触发本插件事件，所有插件中优先级大于此值的事件都将被阻断，因此本插件建议设置较大的值。

### SPARKAPI_IG_SIZE
| 分辨率（可选值） | 消耗图点数 |
|:-----:|:----:|
| [512,512] | 6 |
| [640,360] | 6 |
| [640,480] | 6 |
| [640,640] | 7 |
| [680,512] | 7 |
| [512,680] | 7 |
| [768,768] | 8 |
| [720,1280] | 12 |
| [1280,720] | 12 |
| [1024,1024] | 14 |

### 命令相关：sparkapi_commands、sparkapi_commands_info
- 如有需要，以下命令相关配置项请在`/.venv/Lib/nonebot_plugin_sparkapi/config.py`修改：
  1. sparkapi_commands：指令表
  2. sparkapi_commands_info：指令表说明（用于生成帮助信息）

- 在`config.py`文件中，已经用缩进表示了命令之间的从属关系。一级命令为主命令，二级命令为子命令。

- 命令格式由NoneBot机器人项目下的配置文件`.env`中的`COMMAND_START`和`COMMAND_SEP`决定（请参考NoneBot文档）。默认情况下，`COMMAND_START`为`["/"]`，`COMMAND_SEP`为`["."]`。

- 一级命令会出现在帮助信息中，二级命令在一级命令下出现。

- 以二级命令`preset_create`为例，默认配置下：
  - 预设管理命令`preset`、二级命令`create`。
  - 完整命令格式为`/preset.create`。
  - 这个命令不会出现在`/help`的帮助信息中，但会在发送`/preset`时告知用户命令和用法。

- 当前命令模式还在测试中，如有好的建议欢迎提出。

## 🎉 使用
### 指令表（默认）
以下所有指令均可在config.py中修改，且无需重写菜单/指令生成函数

| 指令（默认配置下） | 说明 |
|:-----:|:----:|
| 直接发送对话内容<br>SPARKAPI_COMMAND_CHAT（若不为空）+对话内容 | 与机器人进行对话 |
| /help | 显示帮助信息 |
| /preset | 显示人物预设菜单和预设相关命令项 |
| /preset.create | 创建自定义人物预设 |
| /preset.set | 选择人物预设并切换 |
| /preset.show | 显示自定义人物预设详情 |
| /preset.delete | 删除自定义人物预设 |
| /session | 显示保存的对话记录和会话管理相关命令项 |
| /session.save | 保存当前对话上下文 |
| /session.load | 加载保存的对话上下文 |
| /session.show | 显示保存的对话记录 |
| /session.delete | 删除保存的对话记录 |
| /clear | 清除当前对话上下文 |
| /image | AI绘图 |
| /ppt | AI生成PPT |

### 自带人物预设
1. 智能助手（默认）
2. 李白

### 效果图
![Demo](https://source.cclmsy.cc/Images/nbp_Sparkapi/demo.png)
[DemoPPT: 科大讯飞星火语言模型项目汇报.pptx](https://source.cclmsy.cc/Images/nbp_Sparkapi/科大讯飞星火语言模型项目汇报.pptx)

## 📝 更新日志
- 2024.7.10 v2.0.0
  - 项目重写
  - 支持会话存储和加载、会话管理
  - 支持预设和历史记录持久化（基于json）
  - 优化命令、功能的实现方式
  - 调整了配置项和指令表
- 2024.6.30 v1.5.0
  - 适配星火4.0API
- 2024.6.25 v1.4.5
  - 使用默认的SSL证书
- 2024.6.9 v1.4.4
  - 优化项目结构
  - 优化部分功能的实现方式
- 2024.5.30 v1.4.1
  - 新增AI生成PPT功能
- 2024.5.29 v1.4.0
  - 项目重构
  - 新增AI绘图功能
- 2024.5.17 v1.2.0
  - 简化了初始命令
  - 模块结构优化
- 2024.5.16 v1.1.0
  - 存储和加载单次会话（基于pickle）
  - 改用异步方式请求API
- 2024.5.15 v1.0.0
  - 支持AI对话
  - 支持上下文关联
  - 支持自定义预设、预设管理