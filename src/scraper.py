#!/usr/bin/env python3
"""
Hustle Scout - AI 副业项目自动获取工具
"""

import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# 需要配置
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "pppeng11@foxfox.com")
SMTP_AUTH_CODE = os.environ.get("SMTP_AUTH_CODE", "")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "936071937@qq.com")

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def search_ai_projects():
    """通过 Claude WebSearch 搜索 AI 副业项目"""
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        response = client.beta.messages.create(
            model="claude-sonnet-4-6-20250514",
            max_tokens=2048,
            tools=[{"type": "web_search"}],
            messages=[{
                "role": "user",
                "content": """搜索当前最新的 AI 副业项目，要求：
1. 适合个人或小团队操作
2. 可以通过 AI 实现全自动或半自动
3. 有明确的变现路径
4. 不需要大量初始资金

请搜索 2026 年 6 月最新的 AI 副业项目，整理 3-5 个项目，每个项目包含：项目名称、自动化程度（用星级如★★★★★表示）、变现路径、所需技能、项目简述（50字内）、以及该项目的信息来源链接。

输出格式要求：
- 每个项目后面必须附上来源链接，格式：🔗 链接：[URL]
- 链接优先使用中文网站（如知乎、微信公众号文章、简书、少数派等），其次是通用技术网站
- 链接必须是有效的网页地址
"""
            }]
        )

        for content in response.content:
            if content.type == "text":
                return content.text
            elif content.type == "web_search":
                return content.text

        return response.content[0].text if hasattr(response.content[0], 'text') else str(response.content)

    except ImportError:
        return """由于网络限制，当前无法访问 Claude API。

## 备选方案：手动添加项目

### 项目 1：AI 内容批量生产工具
- 自动化程度：★★★★★
- 变现路径：SaaS 订阅
- 所需技能：AI API + 前端
- 项目简述：用 AI 自动生成文章、视频脚本等内容，批量发布到自媒体平台变现
🔗 链接：[查看详情](https://www.zhihu.com/topic/AI内容创作)

### 项目 2：AI 电商图片生成
- 自动化程度：★★★★☆
- 变现路径：服务外包
- 所需技能：Stable Diffusion + 电商运营
- 项目简述：为电商卖家批量生成商品主图和详情页图片，按套收费
🔗 链接：[查看详情](https://www.jianshu.com/search?q=AI电商设计)

### 项目 3：AI 论文润色服务
- 自动化程度：★★★★☆
- 变现路径：按篇收费
- 所需技能：AI 写作工具 + 学术知识
- 项目简述：帮研究人员润色学术论文语法和表达，按字数收费
🔗 链接：[查看详情](https://www.zhihu.com/search?query=AI论文润色)

（配置 ANTHROPIC_API_KEY 后可自动搜索最新项目）"""
    except Exception as e:
        return f"搜索出错: {str(e)}"


def generate_markdown(projects_text: str) -> str:
    """生成 Markdown 报告"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    template = f"""# Hustle Scout - {today}

> 自动获取 | AI 全自动副业项目

---

## 今日项目

{projects_text}

---

*由 Hustle Scout 自动生成*
"""

    return template


def save_report(content: str) -> Path:
    """保存报告到文件"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    file_path = REPORTS_DIR / f"{today}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def generate_html_email(markdown_content: str) -> str:
    """将 Markdown 内容转换为美观的 HTML 邮件"""
    import re

    today = datetime.now().strftime("%Y-%m-%d")

    # 简单的 Markdown 转 HTML
    html = markdown_content

    # 处理标题
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # 处理项目（提取项目信息生成卡片）
    project_cards = []
    current_project = {}

    lines = html.split('\n')
    for line in lines:
        if line.startswith('### 项目'):
            if current_project:
                project_cards.append(current_project)
            current_project = {'name': line.replace('###', '').strip()}
        elif '自动化程度' in line:
            current_project['rating'] = line.split('：')[1] if '：' in line else ''
        elif '变现路径' in line:
            current_project['path'] = line.split('：')[1] if '：' in line else ''
        elif '所需技能' in line:
            current_project['skills'] = line.split('：')[1] if '：' in line else ''
        elif '🔗 链接' in line:
            match = re.search(r'\[(.*?)\]\((.*?)\)', line)
            if match:
                current_project['link'] = match.group(2)
                current_project['link_text'] = match.group(1)
        elif '项目简述' in line:
            current_project['desc'] = line.split('：')[1] if '：' in line else ''

    if current_project:
        project_cards.append(current_project)

    # 生成项目卡片 HTML
    cards_html = ''
    for i, p in enumerate(project_cards, 1):
        link_html = f'<a href="{p.get("link", "#")}" target="_blank" class="link-btn">🔗 {p.get("link_text", "查看详情")}</a>' if p.get('link') else ''
        desc_html = f'<div class="project-desc">{p.get("desc", "")}</div>' if p.get('desc') else ''
        cards_html += f'''
        <div class="project-card">
            <div class="project-header">
                <span class="project-num">项目 {i}</span>
                <span class="project-rating">{p.get("rating", "")}</span>
            </div>
            <h4 class="project-name">{p.get("name", "")}</h4>
            {desc_html}
            <div class="project-detail">
                <div><strong>变现路径：</strong>{p.get("path", "")}</div>
                <div><strong>所需技能：</strong>{p.get("skills", "")}</div>
            </div>
            <div class="card-footer">{link_html}</div>
        </div>
        '''

    # 完整的 HTML 邮件模板
    full_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background: #ffffff;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #6366f1;
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            color: #1f2937;
            font-size: 24px;
            margin: 0 0 8px 0;
        }}
        .header .subtitle {{
            color: #6b7280;
            font-size: 14px;
        }}
        .date-badge {{
            display: inline-block;
            background: #6366f1;
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            margin-top: 12px;
        }}
        .projects-section h2 {{
            color: #1f2937;
            font-size: 18px;
            margin-bottom: 16px;
        }}
        .project-card {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        .project-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .project-num {{
            background: #6366f1;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .project-rating {{
            color: #f59e0b;
            font-size: 14px;
        }}
        .project-name {{
            color: #1f2937;
            font-size: 18px;
            margin: 0 0 12px 0;
        }}
        .project-detail {{
            color: #4b5563;
            font-size: 14px;
            line-height: 1.8;
        }}
        .project-detail strong {{
            color: #374151;
        }}
        .project-desc {{
            color: #6366f1;
            font-size: 14px;
            background: #ede9fe;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 12px;
        }}
        .card-footer {{
            display: flex;
            justify-content: flex-end;
            margin-top: 12px;
        }}
        .link-btn {{
            color: #6366f1;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        }}
        .link-btn:hover {{
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            color: #9ca3af;
            font-size: 12px;
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🤖 Hustle Scout</h1>
            <p class="subtitle">AI 全自动副业项目日报</p>
            <span class="date-badge">{today}</span>
        </div>

        <div class="projects-section">
            <h2>📋 今日项目</h2>
            {cards_html}
        </div>

        <div class="footer">
            由 Hustle Scout 自动生成<br>
            每早 9:00 UTC 准时送达
        </div>
    </div>
</body>
</html>'''

    return full_html


def send_email(subject: str, body: str):
    """通过 QQ 邮箱 SMTP 发送 HTML 邮件"""
    if not SMTP_AUTH_CODE:
        print("未配置 SMTP_AUTH_CODE，跳过邮件发送")
        return

    html_content = generate_html_email(body)

    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    # 添加 HTML 内容
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_AUTH_CODE)
            server.send_message(msg)
        print(f"邮件已发送至 {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")


def main():
    print("🔍 搜索 AI 副业项目...")
    projects_text = search_ai_projects()

    print("📝 生成 Markdown 报告...")
    markdown_content = generate_markdown(projects_text)

    print("💾 保存报告...")
    report_path = save_report(markdown_content)
    print(f"报告已保存: {report_path}")

    print("📧 发送邮件...")
    send_email(
        subject=f"Hustle Scout 日报 - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        body=markdown_content
    )

    print("✅ 完成！")


if __name__ == "__main__":
    main()