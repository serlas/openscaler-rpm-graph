import requests
import gzip
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request
import networkx as nx
from io import BytesIO

app = Flask(__name__)

RPM_URL = "https://repo.openscaler.ru/openScaler-22.03-LTS-SP2/OS/x86_64/repodata/primary.xml.gz"
SRPM_URL = "https://repo.openscaler.ru/openScaler-22.03-LTS-SP2/source/repodata/primary.xml.gz"

def parse_repodata(url):
    resp = requests.get(url)
    with gzip.GzipFile(fileobj=BytesIO(resp.content)) as f:
        tree = ET.parse(f)
    root = tree.getroot()
    graph = nx.DiGraph()
    for pkg in root.findall('.//{http://linux.duke.edu/metadata/common}package'):
        name = pkg.find('{http://linux.duke.edu/metadata/common}name').text
        graph.add_node(name)
        requires = pkg.findall('.//{http://linux.duke.edu/metadata/common}requires/{http://linux.duke.edu/metadata/common}reqname')
        for req in requires:
            dep = req.text
            if dep:
                graph.add_edge(name, dep)
    return graph

# Build graphs
runtime_graph = parse_repodata(RPM_URL)
build_graph = parse_repodata(SRPM_URL)

@app.route('/graph/<graph_type>/<pkg>')
def get_deps(graph_type, pkg):
    g = runtime_graph if graph_type == 'runtime' else build_graph
    if pkg not in g:
        return jsonify({'error': 'Package not found'})
    deps = list(nx.descendants(g, pkg))
    return jsonify({'package': pkg, 'dependencies': list(deps)})

@app.route('/visual/<graph_type>/<pkg>')
def get_dot(graph_type, pkg):
    g = runtime_graph if graph_type == 'runtime' else build_graph
    subgraph = nx.ego_graph(g, pkg, radius=2)
    dot = nx.nx_pydot.to_pydot(subgraph).to_string()
    return jsonify({'dot': dot})

if __name__ == '__main__':
    app.run(debug=True)