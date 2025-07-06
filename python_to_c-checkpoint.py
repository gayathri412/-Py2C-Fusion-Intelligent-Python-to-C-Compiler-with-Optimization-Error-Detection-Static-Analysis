import re

def translate_python_to_c(code):
    print("🔁 Translating Python to C:")
    lines = code.strip().split('\n')
    c_code = ['#include <stdio.h>', '#include <math.h>', '']
    indent_level = 0
    indent = lambda: "    " * indent_level

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("print("):
            content = stripped[6:-1].strip()
            c_code.append(f'{indent()}printf("{content}\\n");')
        elif "=" in stripped:
            var, val = stripped.split("=", 1)
            var, val = var.strip(), val.strip()
            c_code.append(f"{indent()}int {var} = {val};")
        elif stripped.startswith("def "):
            name = re.match(r"def (\w+)\(", stripped).group(1)
            c_code.append(f"{indent()}void {name}() {{")
            indent_level += 1
        elif stripped.startswith("return "):
            c_code.append(f"{indent()}return {stripped.split(' ', 1)[1]};")
        elif not line.startswith(" ") and indent_level > 0:
            indent_level -= 1
            c_code.append("}")
    while indent_level > 0:
        indent_level -= 1
        c_code.append("}")
    print("\n".join(c_code))
    return "\n".join(c_code)

if __name__ == "__main__":
    sample = "def greet():\n    print('Hi')\n    return 1"
    translate_python_to_c(sample)

