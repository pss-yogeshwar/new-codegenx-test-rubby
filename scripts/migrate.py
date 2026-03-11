import os
import requests
import sys
from pathlib import Path

# ================================
# CONFIG & ENVS
# ================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SOURCE_LANGUAGE = os.getenv("SOURCE_LANGUAGE", "ruby").lower()
TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", "csharp").lower()

# normalize language names
TARGET_LANGUAGE = TARGET_LANGUAGE.replace("+", "p")  # c++ -> cpp

if not GROQ_API_KEY:
    print("[ERROR] GROQ_API_KEY not set")
    sys.exit(1)

MODEL = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ================================
# LANGUAGE EXTENSIONS
# ================================
LANGUAGE_EXTENSIONS = {
    "ruby": ".rb",
    "python": ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "java": ".java",
    "csharp": ".cs",
    "cpp": ".cpp",
    "c++": ".cpp",
    "go": ".go",
    "php": ".php",
    "foxpro": ".prg"
}

SOURCE_EXT = LANGUAGE_EXTENSIONS.get(SOURCE_LANGUAGE, ".txt")
TARGET_EXT = LANGUAGE_EXTENSIONS.get(TARGET_LANGUAGE, ".txt")

SOURCE_DIR = Path(".")
OUT_DIR = Path("converted-code")
OUT_DIR.mkdir(exist_ok=True)

# ================================
# HELPERS
# ================================
def clean_text(s):
    return "".join(c for c in s if c == "\n" or (32 <= ord(c) <= 126))


def clean_ai_output(text):
    markers = [
        "```csharp","```cs","```python","```py","```javascript","```js",
        "```go","```java","```cpp","```c++","```ruby","```rb","```"
    ]
    for m in markers:
        text = text.replace(m, "")
    return text.strip()


def groq_call(prompt):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 4096
    }

    r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=90)
    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"]


def migrate_code(code, src_lang, tgt_lang):
    prompt = f"""
Convert the following code from {src_lang} to {tgt_lang}.
Return ONLY the raw {tgt_lang} source code.
Do NOT include markdown backticks.

SOURCE CODE ({src_lang}):
{code}
"""
    return groq_call(prompt)


# ================================
# MAIN
# ================================
def main():

    print(f"[START] Migration {SOURCE_LANGUAGE.upper()} -> {TARGET_LANGUAGE.upper()}")

    print("[STEP 1] Scanning source files")

    files = [
        f for f in SOURCE_DIR.rglob(f"*{SOURCE_EXT}")
        if ".git" not in f.parts
        and "node_modules" not in f.parts
        and OUT_DIR not in f.parents
    ]

    if not files:
        print(f"[ERROR] No {SOURCE_LANGUAGE} files found")
        sys.exit(1)

    print(f"[INFO] Found {len(files)} source files")

    errors = 0

    for f in files:

        if f.name.startswith("."):
            continue

        print(f"[STEP 2] Converting: {f}")

        try:

            raw_content = f.read_text(errors="ignore")

            source_code = clean_text(raw_content)

            migrated_content = clean_ai_output(
                migrate_code(source_code, SOURCE_LANGUAGE, TARGET_LANGUAGE)
            )

            out_file = OUT_DIR / (f.stem + TARGET_EXT)

            print(f"[STEP 3] Writing: {out_file}")

            out_file.write_text(migrated_content, encoding="utf-8")

        except Exception as e:

            print(f"[ERROR] Failed converting {f.name}: {str(e)}")

            errors += 1

    if errors > 0:
        print(f"[ERROR] {errors} file(s) failed")
        sys.exit(1)

    print("[SUCCESS] Migration completed successfully")


if __name__ == "__main__":
    main()