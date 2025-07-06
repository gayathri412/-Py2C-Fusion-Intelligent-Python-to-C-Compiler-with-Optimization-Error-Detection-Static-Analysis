def optimize_c_code(code):
    print("🚀 Optimizing C Code:")
    optimized = []
    for line in code.split('\n'):
        if line.strip() and line.strip() != ";":
            optimized.append(line)
    print("\n".join(optimized))
    return "\n".join(optimized)

if __name__ == "__main__":
    sample = "#include <stdio.h>\nint x = 5;\n;"
    optimize_c_code(sample)
