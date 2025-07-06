import re

def lexical_analysis(code):
    print("🔍 Lexical Analysis:")
    tokens = re.findall(r'\b\w+\b|[^\s\w]', code)
    print("Tokens:", tokens)
    return tokens

if __name__ == "__main__":
    sample = "def add(a, b): return a + b"
    lexical_analysis(sample)
