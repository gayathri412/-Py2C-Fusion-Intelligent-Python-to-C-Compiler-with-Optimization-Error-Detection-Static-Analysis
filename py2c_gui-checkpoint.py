import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import ast

# -------------------------
# Compilation Phases
# -------------------------
def lexical_analysis(code):
    tokens = re.findall(r'\b\w+\b|[^\s\w]', code)
    return tokens

def check_syntax(code):
    try:
        ast.parse(code)
        return "✔ No syntax errors."
    except SyntaxError as e:
        return f"❌ Syntax Error: {e}"

class UnreachableCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.messages = []

    def visit_FunctionDef(self, node):
        has_return = False
        for stmt in node.body:
            if has_return:
                self.messages.append(f"⚠ Unreachable code at line {stmt.lineno}")
            if isinstance(stmt, ast.Return):
                has_return = True
        self.generic_visit(node)

def semantic_analysis(code):
    tree = ast.parse(code)
    visitor = UnreachableCodeVisitor()
    visitor.visit(tree)
    if "eval(" in code or "exec(" in code:
        visitor.messages.append("⚠ Warning: Use of eval/exec is insecure.")
    return "\n".join(visitor.messages)

temp_count = 0
def get_temp():
    global temp_count
    t = f"t{temp_count}"
    temp_count += 1
    return t

def generate_TAC(code):
    tree = ast.parse(code)
    tac_lines = []

    class TACVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if isinstance(node.value, ast.BinOp):
                left = getattr(node.value.left, 'id', getattr(node.value.left, 'n', '?'))
                right = getattr(node.value.right, 'id', getattr(node.value.right, 'n', '?'))
                op = type(node.value.op).__name__
                op_map = {'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/'}
                temp = get_temp()
                tac_lines.append(f"{temp} = {left} {op_map.get(op, '?')} {right}")
                tac_lines.append(f"{node.targets[0].id} = {temp}")
            elif isinstance(node.value, ast.Constant):
                tac_lines.append(f"{node.targets[0].id} = {node.value.value}")
    TACVisitor().visit(tree)
    return "\n".join(tac_lines)

def translate_python_to_c(code):
    lines = code.strip().split('\n')
    translated = ['#include <stdio.h>', '#include <math.h>', '']
    indent_level = 0
    declared_vars = {}
    indent = lambda: "    " * indent_level

    for line in lines:
        original = line
        line = re.sub(r"(\w+)\s*\*\*\s*(\w+)", r"pow(\1, \2)", line)
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("def "):
            func = re.match(r"def (\w+)\((.*?)\):", stripped)
            if func:
                name, args = func.groups()
                args_c = ", ".join([f"int {a.strip()}" for a in args.split(",") if a.strip()])
                translated.append(f"{indent()}int {name}({args_c}) {{")
                indent_level += 1
        elif stripped.startswith("return"):
            val = stripped[len("return"):].strip()
            val = "1" if val == "True" else "0" if val == "False" else val
            translated.append(f"{indent()}return {val};")
        elif stripped.startswith("if "):
            cond = stripped[3:].rstrip(":").replace("and", "&&").replace("or", "||").replace("not", "!")
            translated.append(f"{indent()}if ({cond}) {{")
            indent_level += 1
        elif stripped.startswith("elif "):
            indent_level -= 1
            cond = stripped[5:].rstrip(":").replace("and", "&&").replace("or", "||").replace("not", "!")
            translated.append(f"{indent()}}} else if ({cond}) {{")
            indent_level += 1
        elif stripped.startswith("else"):
            indent_level -= 1
            translated.append(f"{indent()}}} else {{")
            indent_level += 1
        elif stripped.startswith("while "):
            cond = stripped[6:].rstrip(":")
            translated.append(f"{indent()}while ({cond}) {{")
            indent_level += 1
        elif "for " in stripped and "in range(" in stripped:
            match = re.match(r"for (\w+) in range\((.*?)\):", stripped)
            if match:
                var, expr = match.groups()
                parts = [p.strip() for p in expr.split(",")]
                if len(parts) == 1:
                    translated.append(f"{indent()}for (int {var} = 0; {var} < {parts[0]}; {var}++) {{")
                elif len(parts) == 2:
                    translated.append(f"{indent()}for (int {var} = {parts[0]}; {var} < {parts[1]}; {var}++) {{")
                elif len(parts) == 3:
                    translated.append(f"{indent()}for (int {var} = {parts[0]}; {var} < {parts[1]}; {var} += {parts[2]}) {{")
                indent_level += 1
        elif "input(" in stripped:
            match = re.match(r"(\w+)\s*=\s*int\s*\(\s*input\s*\((.*)\)\s*\)", stripped)
            if match:
                var, prompt = match.groups()
                prompt = prompt.strip().strip('"').strip("'")
                translated.append(f'{indent()}printf("{prompt}");')
                translated.append(f'{indent()}scanf("%d", &{var});')
                declared_vars[var] = "int"
        elif stripped.startswith("print(f"):
            inner = stripped[7:-1]
            fmt = re.sub(r"\{(\w+)\}", r"%d", inner)
            args = ", ".join(re.findall(r"\{(\w+)\}", inner))
            translated.append(f'{indent()}printf("{fmt}\\n", {args});')
        elif stripped.startswith("print("):
            val = stripped[6:-1].strip()
            if val.startswith('"') or val.startswith("'"):
                val = val.strip('"').strip("'")
                translated.append(f'{indent()}printf("{val}\\n");')
            else:
                fmt = "%d" if declared_vars.get(val) == "int" else "%f"
                translated.append(f'{indent()}printf("{fmt}\\n", {val});')
        elif "=" in stripped:
            var, val = [x.strip() for x in stripped.split("=", 1)]
            if var not in declared_vars:
                if re.match(r"^\d+$", val):
                    declared_vars[var] = "int"
                    translated.append(f"{indent()}int {var} = {val};")
                elif re.match(r"^\d+\.\d+$", val):
                    declared_vars[var] = "float"
                    translated.append(f"{indent()}float {var} = {val};")
                elif val in ["True", "False"]:
                    translated.append(f"{indent()}bool {var} = {1 if val == 'True' else 0};")
                else:
                    translated.append(f"{indent()}// Unsupported assignment: {original}")
            else:
                translated.append(f"{indent()}{var} = {val};")
        elif stripped == "pass":
            translated.append(f"{indent()}// pass")
        elif not original.startswith(" ") and indent_level > 0:
            indent_level -= 1
            translated.append(f"{indent()}}}")
        else:
            translated.append(f"{indent()}// Unsupported: {stripped}")

    while indent_level > 0:
        indent_level -= 1
        translated.append(f"{indent()}}}")
    return "\n".join(translated)

def compile_all(code):
    results = {
        "Lexical Analysis": " ".join(lexical_analysis(code)),
        "Syntax Analysis": check_syntax(code),
        "Semantic Analysis": semantic_analysis(code),
        "Three Address Code": generate_TAC(code),
        "C Code": translate_python_to_c(code)
    }
    return results

# -------------------------
# GUI App
# -------------------------
def browse_file(entry, text):
    path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)
        with open(path, "r") as f:
            code = f.read()
            text.delete("1.0", tk.END)
            text.insert(tk.END, code)

def compile_code(entry, text_input, text_output):
    code = text_input.get("1.0", tk.END)
    results = compile_all(code)
    output = "\n\n".join(f"🔷 {title} \n{body}" for title, body in results.items())
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, output)

root = tk.Tk()
root.title("Python to C Compiler - GUI")

tk.Label(root, text="Python File Path:").grid(row=0, column=0, padx=5, pady=5)
entry_file = tk.Entry(root, width=60)
entry_file.grid(row=0, column=1, padx=5)
tk.Button(root, text="Browse", command=lambda: browse_file(entry_file, text_input)).grid(row=0, column=2)

text_input = scrolledtext.ScrolledText(root, width=90, height=15)
text_input.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

tk.Button(root, text="Compile to C", command=lambda: compile_code(entry_file, text_input, text_output), bg="lightblue").grid(row=2, column=1, pady=10)

text_output = scrolledtext.ScrolledText(root, width=90, height=25, bg="#f5f5f5")
text_output.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
