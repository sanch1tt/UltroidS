# Ultroid - Free AI Commands Wrapper (No API Keys Needed)
# Combines GPT-4o, Claude, DeepSeek, Gemini via free backends.

"""
✘ Commands Available -

• {i}gpt <prompt>
    Get response from OpenAI GPT-4o-mini via g4f.

• {i}antr <prompt>
    Get response from Claude Sonnet 4 via puter.com.

• {i}gemini <prompt>
    Get response from Gemini 2.5 Flash via PollinationsAI (g4f).

• {i}deepseek <prompt>
    Get response from DeepSeek R1 via g4f.

✅ No API key needed for any of the above models.
"""

from . import ultroid_cmd
import requests

try:
    from g4f.client import Client
    import g4f
except ImportError:
    raise ImportError("Install g4f: `pip install -U g4f`")


@ultroid_cmd(pattern="gpt( (.*)|$)")
async def chatgpt(event):
    """ChatGPT (gpt-4o-mini) via free backend"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("📝 Please provide a prompt!")

    msg = await event.eor("Thinking with GPT...")

    header = (
        "🌟 **ChatGPT**\n"
        "**Model:** `gpt-4o-mini`\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        f"**Prompt:**\n{prompt}\n\n"
        "**Response:**\n"
    )

    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        reply = response.choices[0].message.content

        if event.client.me.bot:
            await msg.edit(header)
            full = ""
            for word in reply.split():
                full += word + " "
                try:
                    await msg.edit(header + full)
                except Exception:
                    pass
        else:
            await msg.edit(header + reply)

    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")


@ultroid_cmd(pattern="antr( (.*)|$)")
async def claude(event):
    """Claude (Sonnet-4) via puter backend (no key needed)"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("📝 Please provide a prompt!")

    msg = await event.eor("🧠 Thinking with Claude...")

    API_URL = "https://api.puter.com/drivers/call"
    MODEL_NAME = "claude-sonnet-4-20250514"
    AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://docs.puter.com",
        "Referer": "https://docs.puter.com/",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "interface": "puter-chat-completion",
        "driver": "claude",
        "test_mode": False,
        "method": "complete",
        "args": {
            "messages": [{"content": prompt}],
            "model": MODEL_NAME,
            "stream": False
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            content_list = data["result"]["message"]["content"]
            output = "".join([item["text"] for item in content_list if item["type"] == "text"])
            header = (
                "🧠 **Claude AI**\n"
                f"**Model:** `{MODEL_NAME}`\n"
                "➖➖➖➖➖➖➖➖➖➖\n\n"
                f"**Prompt:**\n{prompt}\n\n"
                "**Response:**\n"
            )
            await msg.edit(header + output)
        else:
            await msg.edit(f"❌ Failed! Status: {response.status_code}\n{response.text}")
    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")


@ultroid_cmd(pattern="deepseek( (.*)|$)")
async def deepseek(event):
    """DeepSeek R1 via free g4f backend"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("❌ Please provide a prompt!")

    msg = await event.eor("🤖 Thinking with DeepSeek...")

    header = (
        "🤖 **DeepSeek R1**\n"
        "**Model:** `deepseek-r1`\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        f"**Prompt:**\n{prompt}\n\n"
        "**Response:**\n"
    )

    try:
        client = Client()
        response = client.chat.completions.create(
            model="deepseek-r1",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content

        if event.client.me.bot:
            await msg.edit(header)
            typed = ""
            for word in reply.split():
                typed += word + " "
                try:
                    await msg.edit(header + typed)
                except Exception:
                    pass
        else:
            await msg.edit(header + reply)

    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")


@ultroid_cmd(pattern="gemini( (.*)|$)")
async def gemini(event):
    """Gemini 2.5 Flash via PollinationsAI (g4f)"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("📝 Please provide a prompt!")

    msg = await event.eor("⚡ Asking Gemini Flash...")

    header = (
        "💫 **Gemini AI**\n"
        "**Model:** `gemini-2.5-flash`\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        f"**Prompt:**\n{prompt}\n\n"
        "**Response:**\n"
    )

    try:
        client = Client(provider=g4f.Provider.PollinationsAI, model="gemini-2.5-flash")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        reply = response.choices[0].message.content

        if event.client.me.bot:
            await msg.edit(header)
            full = ""
            for word in reply.split():
                full += word + " "
                try:
                    await msg.edit(header + full)
                except Exception:
                    pass
        else:
            await msg.edit(header + reply)

    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")
