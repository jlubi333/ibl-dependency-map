################################################################################
# Read dependencies
################################################################################

deps = [] # associative list

lines = []
with open("dep.txt", "r") as f:
    lines = f.read().splitlines()
size = len(lines)

i = 0
while i < size:
    node = lines[i]
    i += 1
    if not node:
        continue
    dep_list = []
    while i < size:
        dep = lines[i]
        i += 1
        if not dep.startswith("  "):
            break
        dep_list.append(dep[2:])
    node_group = node.split(".")[0]
    deps.append((node_group, node, dep_list))


node_count = len(deps)

################################################################################
# Output to HTML
################################################################################

print("""\
<html>
  <head>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.0/vis.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.0/vis.min.css"/>

    <style type="text/css">
      #used-by-label {
        display: block;
        position: fixed;
        z-index: 10;
      }
    </style>
  </head>
  <body>
    <label id="used-by-label">Used by? <input type="checkbox" id="used-by"/></label>
    <div id="graph"></div>

    <script type="text/javascript">
      // Code adopted from http://visjs.org/examples/network/exampleApplications/neighbourhoodHighlight.html

      var DEFAULT_EDGE_COLOR = {
        inherit: 'from'
      };

      var DEFAULT_NODE_COLOR = {
        border: 'hsla(240, 40%, 60%, 1)',
        background: 'hsla(240, 40%, 80%, 1)',
        highlight: {
          border: 'hsla(240, 40%, 60%, 1)',
          background: 'hsla(240, 40%, 80%, 1)'
        }
      };
""")

# print nodes
print("      var nodes = [")
for node_group, node, _ in deps:
    print("        {id: '", node, "', label: '", node, "', value: 1, group: '", node_group, "', color: DEFAULT_NODE_COLOR},", sep="")
print("      ];")

print()

# print edges
print("      var edges = [")
for _, node, dep_list in deps:
    for dep in dep_list:
        print("        {from: '", node, "', to: '", dep, "', arrows: 'to'},", sep="")
print("      ];")

print()

# set up graph
print("""\
      var network;
      var allNodes;
      var allEdges;
      var highlightActive = false;

      var nodesDataset = new vis.DataSet(nodes);
      var edgesDataset = new vis.DataSet(edges);

      var usedByCheckbox;

      function redrawAll() {
        var container = document.getElementById('graph');
        var data = {nodes: nodesDataset, edges: edgesDataset};
        var options = {
          nodes: {
            color: DEFAULT_NODE_COLOR
          },
          edges: {
	    color: DEFAULT_EDGE_COLOR
          }
        };

        network = new vis.Network(container, data, options);

        allNodes = nodesDataset.get({returnType: 'Object'});
        allEdges = edgesDataset.get({returnType: 'Object'});

        network.on('click', neighborhoodHighlight);

        usedByCheckbox = document.getElementById("used-by");
      }

      function neighborhoodHighlight(params) {
        var usedBy = usedByCheckbox.checked;
        var hue = usedBy ? '120' : '0';

        // if something is selected:
        if (params.nodes.length > 0) {
          highlightActive = true;
          var selectedNode = params.nodes[0];

          // mark all nodes as hard to read
          for (var nodeId in allNodes) {
            allNodes[nodeId].color = 'rgba(230,230,230,1)';
          }

          // mark all edges as hard to read
          for (var edgeId in allEdges) {
            allEdges[edgeId].color = 'rgba(230,230,230,0.5)';
          }

          var connectedEdges = network.getConnectedEdges(selectedNode)
          var edge, tester, other;

          // recolor

          // edges and fringe nodes
          for (var i = 0; i < connectedEdges.length; i++) {
            edge = allEdges[connectedEdges[i]];
            // only consider correct directionality edges
	    tester = usedBy ? edge.to : edge.from;
            other = usedBy ? edge.from : edge.to;
            if (tester == selectedNode) {
              edge.color = DEFAULT_EDGE_COLOR;
              allNodes[other].color = {
		border: 'hsla(' + hue + ', 40%, 60%, 1)',
		background: 'hsla(' + hue + ', 40%, 80%, 1)'
              };
              allNodes[other].color.highlight = {
		border: 'hsla(' + hue + ', 40%, 60%, 1)',
		background: 'hsla(' + hue + ', 40%, 80%, 1)'
              };
            }
          }
	  // main node
          allNodes[selectedNode].color = {
	    border: 'hsla(' + hue + ', 40%, 40%, 1)',
	    background: 'hsla(' + hue + ', 40%, 60%, 1)'
          };
          allNodes[selectedNode].color.highlight = {
	    border: 'hsla(' + hue + ', 40%, 40%, 1)',
	    background: 'hsla(' + hue + ', 40%, 60%, 1)'
          };
        } else if (highlightActive === true) {
          // reset all nodes and edges
          for (var nodeId in allNodes) {
            allNodes[nodeId].color = DEFAULT_NODE_COLOR;
          }
          for (var edgeId in allEdges) {
            allEdges[edgeId].color = DEFAULT_EDGE_COLOR;
          }
          highlightActive = false
        }

        // transform the node object into an array
        var updateNodeArray = [];
        for (nodeId in allNodes) {
          if (allNodes.hasOwnProperty(nodeId)) {
            updateNodeArray.push(allNodes[nodeId]);
          }
        }
        nodesDataset.update(updateNodeArray);

        // transform the edge object into an array
        var updateEdgeArray = [];
        for (edgeId in allEdges) {
          if (allEdges.hasOwnProperty(edgeId)) {
            updateEdgeArray.push(allEdges[edgeId]);
          }
        }
        edgesDataset.update(updateEdgeArray);
      }

      redrawAll()
    </script>
  </body>
</html>""")
