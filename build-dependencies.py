import os
import json
import sys

def find_kvm_dependencies(kvm_list_str, proxy_dir_path):
    """
    Finds KVM dependencies for each proxy.

    Args:
        kvm_list_str: A string in the format '[ "kvm1", "kvm2", ... ]'.
        proxy_dir_path: The path to the directory containing the proxy directories.

    Returns:
        A dictionary where keys are proxy names and values are lists of KVM names.
    """
    try:
        kvm_list = json.loads(kvm_list_str)  # Convert the string to a list
    except json.JSONDecodeError:
        print("Error: Invalid KVM list format. Please provide a valid JSON string.")
        return {}

    dependencies = {}
    for proxy_name in os.listdir(proxy_dir_path):
        proxy_path = os.path.join(proxy_dir_path, proxy_name)
        if os.path.isdir(proxy_path):
            dependencies[proxy_name] = []
            for root, _, files in os.walk(proxy_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            for kvm_name in kvm_list:
                                if kvm_name in content:
                                    dependencies[proxy_name].append(kvm_name)
                        except UnicodeDecodeError:
                            print(f"Skipping file due to decoding error: {file_path}")

    return dependencies

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python kvm_dependency_finder.py '<KVM_LIST>' <PROXY_DIR_PATH>")
        sys.exit(1)

    kvm_list_string = sys.argv[1]
    proxy_directory = sys.argv[2]

    dependency_map = find_kvm_dependencies(kvm_list_string, proxy_directory)

    for proxy_name, kvm_names in dependency_map.items():
        print(f"{proxy_name}: {', '.join(kvm_names)}")