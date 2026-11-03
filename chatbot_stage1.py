"""
阶段 1 实战：LLM API 对话机器人（覆盖计划里前 4 个任务）
任务：① API 请求  ② 流式输出  ③ 多轮记忆  ④ 错误处理
模型：DeepSeek（便宜，接口与 OpenAI 完全兼容，新手最友好）
"""
import os
from openai import OpenAI

# ---------- 1) 读取 API Key（务必用环境变量，别写死在代码里）----------
# macOS/Linux 终端执行:  export DEEPSEEK_API_KEY="你的key"
# Windows  CMD 执行:     set DEEPSEEK_API_KEY=你的key
# Windows  PowerShell:   $env:DEEPSEEK_API_KEY="你的key"
# Windows 新手若嫌环境变量麻烦，可临时改成：API_KEY = "sk-你的key"（仅本地学习，切勿提交到 GitHub）
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise SystemExit("❌ 请先设置环境变量 DEEPSEEK_API_KEY 再运行（或把上面一行直接赋值为你的 Key）")

# ---------- 2) 初始化客户端（DeepSeek 用 OpenAI 兼容接口）----------
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# ---------- 3) 系统提示词：定义 AI 角色（Prompt 工程第一步）----------
SYSTEM_PROMPT = "你是一个耐心、专业的中文编程助手，回答简洁、有例子。"
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print("=== 聊天开始，输入 exit 退出 ===")
while True:
    try:
        user_input = input("\n你: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not user_input:
        continue
    if user_input.lower() == "exit":
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})

    try:
        # ---------- 4) 流式输出：逐字打印，体验更流畅 ----------
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,        # 开启流式
            temperature=0.7,    # 0=严谨死板，1=发散 creative
        )
        print("AI: ", end="", flush=True)
        full_reply = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            full_reply += delta
        print()
        # ---------- 5) 多轮记忆：把 AI 回复也加回上下文 ----------
        messages.append({"role": "assistant", "content": full_reply})
    except Exception as e:
        # ---------- 6) 错误处理：网络/额度/限流等问题不崩溃 ----------
        print(f"[调用出错] {e}")
        messages.pop()  # 移除这次失败的用户消息，避免污染上下文
