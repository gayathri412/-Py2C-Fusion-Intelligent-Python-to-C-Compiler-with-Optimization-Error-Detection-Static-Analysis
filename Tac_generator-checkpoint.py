import ast

temp_counter = 0
def get_temp():
    global temp_counter
    temp = f"t{temp_counter}"
    temp_counter += 1
    return temp

def generate_TAC(code):
    print("🔃 Three Address Code (TAC):")
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
    for line in tac_lines:
        print(line)

if __name__ == "__main__":
    sample = "x = 1\ny = 2\nz = x + y"
    generate_TAC(sample)
