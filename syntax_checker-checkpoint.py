import ast

def check_syntax(code):
    print("🧠 Syntax Analysis:")
    try:
        tree = ast.parse(code)
        print("✔ No syntax errors.")
        return tree
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        return None

if __name__ == "__main__":
    sample = "def add(a, b): return a + b"
    check_syntax(sample)
