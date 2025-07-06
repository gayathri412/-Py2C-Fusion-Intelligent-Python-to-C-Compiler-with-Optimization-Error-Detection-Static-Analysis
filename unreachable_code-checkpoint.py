import ast

class UnreachableCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node):
        has_return = False
        for stmt in node.body:
            if has_return:
                self.issues.append(f"⚠ Unreachable code at line {stmt.lineno}")
            if isinstance(stmt, ast.Return):
                has_return = True
        self.generic_visit(node)

def semantic_analysis(code):
    print("🧩 Semantic Analysis:")
    tree = ast.parse(code)
    visitor = UnreachableCodeVisitor()
    visitor.visit(tree)
    for issue in visitor.issues:
        print(issue)
    if "eval(" in code or "exec(" in code:
        print("⚠ Warning: Use of eval/exec is insecure.")

if __name__ == "__main__":
    sample = "def f(): return 1\nprint('After return')"
    semantic_analysis(sample)
