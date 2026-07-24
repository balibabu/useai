import ast
import os
import re
from pathlib import Path

# 1. Folders to ignore during scanning
IGNORE_DIRS = {
    ".git",
    ".vs",
    "bin",
    "obj",
    "node_modules",
    "__pycache__",
    ".venv",
    "env",
}

# 2. ONLY scan files with these extensions (lowercase)
ALLOWED_EXTENSIONS = {
    ".cs",
    ".py",
    # Add any other extensions you want to target:
    # ".js",
    # ".ts",
}


def extract_csharp_outline(code: str) -> str:
    """Extracts class, interface, and method signatures from C# code using regex."""
    outline_lines = []

    namespace_pattern = re.compile(r"^\s*namespace\s+[\w\.]+")
    type_pattern = re.compile(
        r"^\s*(public|private|protected|internal|static|abstract|partial|\s)*(class|interface|struct|enum)\s+\w+"
    )
    method_pattern = re.compile(
        r"^\s*(public|private|protected|internal|static|async|virtual|override|abstract|\s)+[\w<>\[\]]+\s+\w+\s*\(.*?\)"
    )

    for line in code.splitlines():
        stripped = line.strip()

        if (
            not stripped
            or stripped.startswith("//")
            or stripped.startswith("using ")
        ):
            continue

        if (
            namespace_pattern.match(line)
            or type_pattern.match(line)
            or method_pattern.match(line)
        ):
            clean_line = line.rstrip("{ ").rstrip()
            outline_lines.append(clean_line)

    return "\n".join(outline_lines)


def extract_python_outline(code: str) -> str:
    """Extracts class and function definitions from Python code using AST."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "  [Error: Could not parse Python file syntax]"

    outline_lines = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            outline_lines.append(f"class {node.name}:")
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            args = [a.arg for a in node.args.args]
            arg_str = ", ".join(args)
            outline_lines.append(f"  def {node.name}({arg_str}):")

    return "\n".join(outline_lines)


def generate_project_outline(
    project_path: str,
    output_txt: str,
    allowed_exts: set = ALLOWED_EXTENSIONS,
):
    root_dir = Path(project_path)

    if not root_dir.exists():
        print(f"Error: Path '{project_path}' does not exist.")
        return

    # Standardize extensions to lowercase with dots (e.g. '.cs')
    target_extensions = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in allowed_exts
    }

    scanned_count = 0

    with open(output_txt, "w", encoding="utf-8") as out:
        out.write(f"PROJECT OUTLINE FOR: {root_dir.resolve()}\n")
        out.write(f"TARGET EXTENSIONS: {', '.join(target_extensions)}\n")
        out.write("=" * 80 + "\n\n")

        for current_path, dirs, files in os.walk(root_dir):
            # Prune ignored directories in place
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file_name in sorted(files):
                file_path = Path(current_path) / file_name
                ext = file_path.suffix.lower()

                # SKIP any file that isn't in our allowed list
                if ext not in target_extensions:
                    continue

                scanned_count += 1
                rel_path = file_path.relative_to(root_dir)

                out.write(f"FILE: {rel_path}\n")
                out.write("-" * 60 + "\n")

                try:
                    content = file_path.read_text(
                        encoding="utf-8", errors="ignore"
                    )

                    if ext == ".cs":
                        outline = extract_csharp_outline(content)
                    elif ext == ".py":
                        outline = extract_python_outline(content)
                    else:
                        outline = "  [No extractor configured for this file type]"

                    out.write(
                        outline if outline else "  (No signatures found)\n"
                    )

                except Exception as e:
                    out.write(f"  [Error reading file: {e}]\n")

                out.write("\n\n")

    print(
        f"Done! Scanned {scanned_count} matching file(s). Outline saved to: {output_txt}"
    )



generate_project_outline(input("enter project path: "), "app_outline.txt")
