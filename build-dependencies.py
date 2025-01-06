# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import sys

def find_kvm_dependencies(kvm_list_str, proxy_dir_path):
    """
    Finds KVM dependencies for each proxy (forward mapping) and
    also creates a reverse mapping of KVMs to proxies.

    Args:
        kvm_list_str: A string in the format '[ "kvm1", "kvm2", ... ]'.
        proxy_dir_path: The path to the directory containing the proxy directories.

    Returns:
        A tuple containing two dictionaries:
        1. forward_dependencies:  Keys are proxy names, values are lists of KVM names.
        2. reverse_dependencies: Keys are KVM names, values are lists of proxy names.
    """
    try:
        kvm_list = json.loads(kvm_list_str)  # Convert the string to a list
    except json.JSONDecodeError:
        print("Error: Invalid KVM list format. Please provide a valid JSON string.")
        return {}, {}

    forward_dependencies = {}
    reverse_dependencies = {kvm_name: [] for kvm_name in kvm_list} # Initialize with empty lists for each KVM

    for proxy_name in os.listdir(proxy_dir_path):
        proxy_path = os.path.join(proxy_dir_path, proxy_name)
        if os.path.isdir(proxy_path):
            forward_dependencies[proxy_name] = []
            for root, _, files in os.walk(proxy_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            for kvm_name in kvm_list:
                                if kvm_name in content:
                                    forward_dependencies[proxy_name].append(kvm_name)
                                    reverse_dependencies[kvm_name].append(proxy_name) # Add proxy to the reverse map
                        except UnicodeDecodeError:
                            print(f"Skipping file due to decoding error: {file_path}")

    return forward_dependencies, reverse_dependencies


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python build-dependencies.py '<KVM_LIST>' <PROXY_DIR_PATH>")
        sys.exit(1)

    kvm_list_string = sys.argv[1]
    proxy_directory = sys.argv[2]

    forward_deps, reverse_deps = find_kvm_dependencies(kvm_list_string, proxy_directory)


    print("Forward Dependencies (Proxy --> KVMs):")
    for proxy_name, kvm_names in forward_deps.items():
        print(f"{proxy_name}: {', '.join(kvm_names)}")

    print("\nReverse Dependencies (KVM --> Proxies):")
    for kvm_name, proxy_names in reverse_deps.items():
        print(f"{kvm_name}: {', '.join(proxy_names)}")
