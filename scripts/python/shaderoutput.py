# a quick shortcut for shader builder, connecting selected node to output directly
# by Lewis Orton
# https://vimeo.com/lewisorton

# instruction: create a new shelftool, copy the code below (not including hashtag) to script tab, then assign a hotkey to the tool
# ____copy code below____

# import shaderoutput
# shaderoutput.connect()

# ____copy code above____


import hou, sys, nodesearch, operator

def connect():
    node_output = None
    nodes = hou.selectedNodes()
    if len(nodes) == 0:
        return False
        
    node = nodes[0]
    network = node.parent()
    renderer = node.type().name().split("::")[0]
    if renderer == "redshift":
        matcher = nodesearch.NodeType("redshift_material",typecat=None, exact=True)
    elif renderer == "arnold":
        matcher = nodesearch.NodeType("arnold_material",typecat=None, exact=True)
    else:
        matcher = nodesearch.NodeType("output",typecat=None, exact=True)
        

    if len(matcher.nodes(network)) == 0:
        print("No output node found")
        return False
    elif len(matcher.nodes(network)) == 1:
        node_output = matcher.nodes(network)[0]
        if node == node_output:
            print("No recursive connection allowed")
            return False
    else:
        #sort all output nodes by distance
        nodes_output = {}
        for node_candidate in matcher.nodes(network):
            distance = (node_candidate.position() - node.position()).lengthSquared()
            nodes_output[node_candidate] = distance

        #python version compatibility
        if sys.version_info[0] < 3:
            nodes_sorted = sorted(nodes_output.items(), key = operator.itemgetter(1))
        else:
            nodes_sorted = sorted(nodes_output.items(), key = lambda kv: kv[1])

        #find output if any node on the right, which should be considered first
        for node_candidate, distance in nodes_sorted:
            if node_candidate.position().x() > node.position().x():
                node_output = node_candidate
                break
        if node_output == None:
            node_output = nodes_sorted[0][0]
    
    node_output.setInput(0, node)

