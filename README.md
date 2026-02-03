# dy-download

> 抖音视频无水印下载 + 语音转文字 + AI 内容摘要

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一款功能强大的抖音视频下载工具，支持无水印下载、音频提取、语音识别和 AI 智能摘要。

## 功能特性

- **无水印下载** - 获取抖音原始高清视频，去除平台水印
- **音频提取** - 自动从视频中提取 MP3 音频
- **语音转文字** - 使用阿里云 DashScope paraformer-v2 模型进行高精度语音识别
- **AI 内容摘要** - 自动生成视频内容的结构化概要，包含核心主题、关键要点、金句提取
- **断点续传** - 支持下载中断后自动恢复
- **Markdown 输出** - 转录内容以美观的 Markdown 格式保存

## 效果展示

```
输入抖音链接
      ↓
   下载视频 (无水印)
      ↓
   提取音频 (MP3)
      ↓
   语音识别 (paraformer-v2)
      ↓
   AI 摘要生成 (qwen-plus)
      ↓
输出结构化文件夹
```

## 环境要求

- Python 3.7+
- ffmpeg (系统需安装)

### 安装 ffmpeg

**Windows:**
```bash
# 使用 Chocolatey
choco install ffmpeg

# 或从官网下载
# https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

## 安装

```bash
# 克隆仓库
git clone https://github.com/ryanfish1/dy-download-skill.git
cd dy-download-skill

# 安装 Python 依赖
pip install -r requirements.txt
```

或手动安装依赖：
```bash
pip install requests ffmpeg-python dashscope
```

## 配置

### 获取阿里云 DashScope API Key

1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 开通 DashScope 服务
3. 创建 API Key

### 设置环境变量

**Windows (PowerShell):**
```powershell
$env:DASHSCOPE_API_KEY="your-api-key-here"
```

**Windows (CMD):**
```cmd
set DASHSCOPE_API_KEY=your-api-key-here
```

**macOS/Linux:**
```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

**永久设置 (推荐):**

在系统环境变量中添加 `DASHSCOPE_API_KEY`

## 使用方法

### 基本用法

```bash
python scripts/download_douyin.py "抖音视频链接"
```

### 指定 API Key

```bash
python scripts/download_douyin.py "抖音视频链接" --api-key "your-api-key"
```

### 支持的链接格式

| 格式 | 示例 |
|------|------|
| 标准链接 | `https://www.douyin.com/video/7602534911685266734` |
| 带参数链接 | `https://www.douyin.com/user/self?modal_id=7602534911685266734` |
| 短链接 | `https://v.douyin.com/xxxxx` |

## 输出结构

下载的文件会保存在 `D:\dydownload\` 目录下：

```
D:\dydownload\
└── {video_id}_{YYYYMMDD_HHMMSS}\      # 时间戳文件夹
    ├── {video_id}.mp4                 # 无水印视频
    ├── {video_id}.mp3                 # 提取的音频
    └── {video_id}.md                  # 转录文字 + AI 摘要
```

### Markdown 文件内容

```markdown
# 抖音视频语音转文字

视频ID: 7602534911685266734
下载时间: 2026-02-04 00:04:58

## 视频内容概要

### 一、核心主题
**传播时代的价值分野：大众连接与批判锋芒之间的文化张力**

### 二、关键要点
- "5% vs 95%"的传播哲学分歧
- 路径分化：桥梁建造者 vs 刺刀反抗者
- 成功背后的异化风险
...

### 三、核心金句
> "好内容不需要俯视或仰视，只需要平视这个时代的真实情绪。"

---

## 完整转录内容
(此处为完整的语音转文字内容)
```

## 使用示例

```bash
# 下载单条视频
python scripts/download_douyin.py "https://www.douyin.com/video/7602534911685266734"

# 使用短链接
python scripts/download_douyin.py "https://v.douyin.com/xxxxx"
```

## 技术栈

| 组件 | 用途 |
|------|------|
| [requests](https://requests.readthedocs.io/) | HTTP 请求 |
| [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) | 音视频处理 |
| [DashScope](https://dashscope.aliyun.com/) | 阿里云百炼 API |
| paraformer-v2 | 语音识别模型 |
| qwen-plus | 内容摘要生成 |

## 作为 Claude Code Skill 使用

如果您使用 [Claude Code](https://claude.ai/code)，可以直接安装此 skill：

```bash
# 将 skill 复制到 Claude skills 目录
cp -r dy-download-skill ~/.claude/skills/dy-download

# 在 Claude Code 中使用
/skill dy-download https://www.douyin.com/video/xxxxx
```

## 常见问题

### Q: 下载失败怎么办？
A: 脚本支持断点续传，重新运行相同命令即可继续下载。

### Q: API 限额用完了怎么办？
A: 阿里云 DashScope 新用户有免费额度，用完后需要充值。

### Q: 转录不准确怎么办？
A: paraformer-v2 模型对中英文识别准确率较高，如遇方言或专业术语可能需要人工校对。

## License

[MIT License](LICENSE)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ryanfish1/dy-download-skill&type=Date)](https://star-history.com/#ryanfish1/dy-download-skill&Date)

---

Made with [heart] by [ryanfish1](https://github.com/ryanfish1)
