import os

def generate_token_efficient_tree(start_dir, indent_size=2, max_depth=None, ignore_dirs=None):
    if ignore_dirs is None:
        # Common heavy folders to exclude
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.DS_Store'}
    
    root_name = os.path.basename(os.path.abspath(start_dir))
    print(f"{root_name}/")
    
    def _walk(current_dir, depth=1):
        # Stop digging deeper if we've hit the maximum depth limit
        if max_depth is not None and depth > max_depth:
            return
            
        try:
            items = sorted(os.listdir(current_dir))
        except PermissionError:
            return

        for item in items:
            if item in ignore_dirs:
                continue
                
            item_path = os.path.join(current_dir, item)
            indent = " " * (depth * indent_size)
            
            if os.path.isdir(item_path):
                print(f"{indent}{item}/")
                _walk(item_path, depth + 1)
            else:
                print(f"{indent}{item}")

    _walk(start_dir)

# Run the script
if __name__ == "__main__":
    # Example: max_depth=2 will show root items and their immediate children only
    path=input('enter path: ')
    generate_token_efficient_tree(path, max_depth=int(input('max depth: ')))
