sample = """
def greet():
    print("Hello")
    return
    print("This won't run")

x = 5
y = 3.14
print(x)
"""

if __name__ == "__main__":
    from analyzer.syntax_checker import check_syntax
    from analyzer.unreachable_code import detect_unreachable_code
    from analyzer.static_analyzer import static_analysis
    from translator.python_to_c import translate_python_to_c
    from optimizer.c_optimizer import optimize_c_code

    print("--- Testing on sample code ---")
    check_syntax(sample)
    detect_unreachable_code(sample)
    static_analysis(sample)

    c_code = translate_python_to_c(sample)
    print("\n--- Translated C Code ---")
    print(c_code)

    print("\n--- Optimized C Code ---")
    print(optimize_c_code(c_code))
