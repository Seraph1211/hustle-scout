# Hustle Scout

每天自动获取适合 AI 全自动完成的副业项目，生成 Markdown 报告并发送邮件。

## 功能

- 🤖 自动搜索最新 AI 副业项目
- 📝 生成 Markdown 格式日报
- 📧 通过 QQ 邮箱发送邮件
- ⏰ 每天 9:00 UTC 自动运行

## 配置

### 1. 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

| 名称 | 说明 |
|------|------|
| `ANTHROPIC_API_KEY` | Claude API 密钥（可选，不配置则使用备选内容） |
| `SMTP_EMAIL` | 发送邮箱地址 |
| `SMTP_AUTH_CODE` | QQ 邮箱授权码 |
| `RECIPIENT_EMAIL` | 接收邮件的邮箱地址 |

### 2. 启用 GitHub Actions

推送代码后，GitHub Actions 会自动运行。也可以手动触发：

1. 进入 Actions 页面
2. 选择 "Daily Hustle Scout"
3. 点击 "Run workflow"

## 本地测试

```bash
cd hustle-scout
pip install anthropic requests

export SMTP_EMAIL="your@qq.com"
export SMTP_AUTH_CODE="your_auth_code"
export RECIPIENT_EMAIL="recipient@example.com"

python src/scraper.py
```

## 项目结构

```
hustle-scout/
├── .github/workflows/daily-scout.yml  # GitHub Actions 工作流
├── src/scraper.py                      # 主程序
├── templates/daily-report.md          # 报告模板
└── reports/                            # 生成的报告
    └── 2026-06-08.md
```

## 邮件效果

邮件包含当日 Markdown 报告的完整内容，可直接查看。完整报告也保存在 `reports/` 目录。