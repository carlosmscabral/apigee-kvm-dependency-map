import networkx as nx
import matplotlib.pyplot as plt
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


def create_dependency_graph(dependencies, graph_type="forward"):
    """
    Creates a NetworkX graph from the dependency data.

    Args:
        dependencies: A dictionary representing the dependencies.
        graph_type: Either "forward" (proxy -> KVM) or "reverse" (KVM -> proxy).

    Returns:
        A NetworkX directed graph (DiGraph).
    """
    graph = nx.DiGraph()

    if graph_type == "forward":
        for proxy_name, kvm_names in dependencies.items():
            for kvm_name in kvm_names:
                graph.add_edge(proxy_name, kvm_name)  # Add edges from proxy to KVM
    elif graph_type == "reverse":
        for kvm_name, proxy_names in dependencies.items():
            for proxy_name in proxy_names:
                graph.add_edge(kvm_name, proxy_name)  # Add edges from KVM to proxy
    else:
        raise ValueError("Invalid graph_type. Must be 'forward' or 'reverse'")

    return graph

def draw_dependency_graph(graph, graph_type):
    """
    Draws and displays the dependency graph.
    """
    plt.figure(figsize=(12, 8))  # Adjust figure size as needed
    plt.title(f"{graph_type.capitalize()} Dependencies")

    # Use a layout algorithm for better visualization (e.g., spring_layout)
    pos = nx.spring_layout(graph, k=0.5, iterations=50)  

    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color="skyblue",
            font_size=10, font_weight="bold", arrowsize=20)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # ... (rest of your main block)
    forward_deps, reverse_deps = find_kvm_dependencies(kvm_list_string, proxy_directory)

    # Create and draw the forward dependency graph
    forward_graph = create_dependency_graph(forward_deps, "forward")
    draw_dependency_graph(forward_graph, "forward")

    # Create and draw the reverse dependency graph
    reverse_graph = create_dependency_graph(reverse_deps, "reverse")
    draw_dependency_graph(reverse_graph, "reverse")