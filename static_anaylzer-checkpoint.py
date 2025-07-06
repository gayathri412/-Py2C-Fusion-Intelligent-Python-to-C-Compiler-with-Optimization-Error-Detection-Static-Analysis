def static_analysis(code):
    if "eval(" in code or "exec(" in code:
        print("⚠ Use of eval/exec detected. This can be insecure.")
    if "import os" in code:
        print("🔎 Note: os module usage found. Ensure sandboxing if needed.")
