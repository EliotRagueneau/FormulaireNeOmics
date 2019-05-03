# Powered by Python 3.5

# To cancel the modifications performed by the script
# on the current graph, click on the undo button.

# Some useful keyboards shortcuts :
#   * Ctrl + D : comment selected lines.
#   * Ctrl + Shift + D  : uncomment selected lines.
#   * Ctrl + I : indent selected lines.
#   * Ctrl + Shift + I  : unindent selected lines.
#   * Ctrl + Return  : run script.
#   * Ctrl + F  : find selected text.
#   * Ctrl + R  : replace selected text.
#   * Ctrl + Space  : show auto-completion dialog.

from tulip import tlp
import re
import math
from math import pi

import statistics


# The updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# The pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the "Run script " button.

# The runGraphScript(scriptFile, graph) function can be called to launch
# another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call (in the form [a-zA-Z0-9_]+.py)

# The main(graph) function must be defined
# to run the script on the current graph


def assignLabelFromPropty(graph, propty_source, propty_target):
    """
    Assign the value of a property into an other property.

    Args:
        graph (tlp.Graph): Graph containing both property.
        propty_source (tlp.GraphProperty): Property whose value is copied.
        propty_target (tlp.GraphProperty): Property whose value is paste.
    """
    for node in graph.getNodes():
        if propty_source[node] != "":
            propty_target[node] = propty_source[node]


def assignNodeSize(graph, propty_size, size):
    """
    Assign a size for all the nodes in the graph.

    Args:
        graph (tlp.Graph): Graph containing all nodes
        propty_size (tlp.SizeProperty): Property holding size of the nodes
        size (int): Int value for size
    """
    for node in graph.getNodes():
        propty_size[node] = tlp.Size(size)


def setAllRegulationStyle(graph, propty_negative, propty_positive, localColor):
    """
    Set edges color based on regulation interaction: positive or negative (or both).

    Args:
        graph (tlp.Graph): A graph object.
        propty_negative (tlp.BooleanProperty): Edges boolean property for negative regulation
        propty_positive (tlp.BooleanProperty): Edges boolean property for positive regulation
        localColor (boolean): True (colors will be local) or False (colors will be applied on parents graph)
    """
    if localColor == True:
        propty_color = graph.getLocalColorProperty("viewColor")
    else:
        propty_color = graph.getColorProperty("viewColor")
    for e in graph.getEdges():
        if propty_negative[e] == True and propty_positive[e] == False:
            propty_color[e] = tlp.Color(255, 0, 0)
        elif propty_negative[e] == False and propty_positive[e] == True:
            propty_color[e] = tlp.Color(0, 0, 255)
        elif propty_negative[e] == True and propty_positive[e] == True:
            propty_color[e] = tlp.Color(0, 255, 0)
        else:
            propty_color[e] = tlp.Color(0, 0, 0)


def drawWithAlgo(graph, layout, algo):
    """
    Run an existing Tulip's layout algorithm on graph

    Args:
        graph (tlp.Graph): A graph object.
        layout (tlp.LayoutProperty): Layout property assigned
        algo (string): The name of the Tulip's algorithm executed.
    """
    graph.applyLayoutAlgorithm(algo, layout)


def deleteSubGraph(graph, subgraph_name):
    """
    Delete a subgraph.

    Args:
        graph (tlp.Graph):  A graph object.
        subgraph_name (string): The name of the subgraph.
    """
    subgraph = graph.getSubGraph(subgraph_name)
    if subgraph != None:
        graph.delSubGraph(subgraph)


def createclusterTree(graph, subgraph_starter):
    """
    Create a tree and call a recursive function that draw on it the hierarchical structure of a graph and it's subgraphs

    Args:
        graph (tlp.Graph): The root graph
        subgraph_starter (string): The name of the graph (or subgraph) on the top of the hierarchy of interest.
    """
    visitedCluster = 0
    deleteSubGraph(graph, "Cluster Hierarchy")  # delete subgraph if it already exist.
    tree = graph.addSubGraph("Cluster Hierarchy")
    firstNode = tree.addNode()
    for subgraph in graph.getSubGraph(subgraph_starter).getSubGraphs():
        clusterTreeConstruction(tree, firstNode, subgraph)


def clusterTreeConstruction(tree, local_root_node, cluster):
    """
    Recursively, add nodes to the tree for each subgraph/cluster and add leaf-node for each node in last level-subgraphs

    Args:
        tree (tlp.Graph): The tree holding the hierarchical structure
        local_root_node (tlp.node): Current tree's node in the course of the recursive function.
        cluster (tlp.Graph): The current subgraph observed
    """
    newNode = tree.addNode()
    tree.addEdge(local_root_node, newNode)

    if cluster.numberOfSubGraphs() < 1:
        for n in cluster.getNodes():
            tree.addNode(n)
            tree.addEdge(newNode, n)
        return

    subgraphs = cluster.getSubGraphs()
    for subgraph in subgraphs:
        clusterTreeConstruction(tree, newNode, subgraph)


def setRadialLayout(graph, layout):
    """
    Apply the Tulip's radial layout on graph.

    Args:
        graph (tlp.Graph): A graph object.
        layout (tlp.LayoutProperty): Layout property assigned
    """
    drawWithAlgo(graph.getSubGraph("Cluster Hierarchy"), layout, "Tree Radial")


def colorByProperty(graph, propty_double, localColor, min_propty_value, max_propty_value):
    """
    Color each node of the graph by generating a gradient with a min and max value.

    Args:
        graph (tlp.Graph): A graph object.
        propty_double (tlp.DoubleProperty): Graph property holding value for the color
        localColor (boolean):  True (colors will be local) or False (colors will be applied on parents graph)
        min_propty_value (int): Minimum value for the gradient
        max_propty_value (int): Maximum value for the gradient
    """
    if localColor == True:
        propty_color = graph.getLocalColorProperty("viewColor")
    else:
        propty_color = graph.getColorProperty("viewColor")
    colorScale = tlp.ColorScale([])
    colorScale.setColorScale([tlp.Color.Red, tlp.Color.Black, tlp.Color.Green], gradient=True)
    for node in graph.getNodes():
        # reduce interval of double values from [minValue,maxValue] to [0,1]
        position_on_scale = (propty_double[node] - min_propty_value) / (max_propty_value - min_propty_value)
        calculated_color = colorScale.getColorAtPos(position_on_scale)
        propty_color[node] = calculated_color


def findShortestPathTree(tree, node_source, node_target):
    """
    In a tree the shortest path between two nodes, pass through their common ancestor.
    This function search the shortest path by adding the depth of each node from this ancestor

    Args:
        tree (tlp.Graph): A graph object.
        node_source (tlp.node): Source node
        node_target (tlp.node): Target node

    Returns:
        path (list): A list of node in the path from node_source to node_target
    """
    common_ancestor = findCommonAncestor(tree, node_source, node_target)
    path_from_source = []
    path_from_target = []
    # get ancestors of each node in the tree and add it to path
    for node in [node_source, node_target]:
        if node != common_ancestor:
            ancestors = findAncestors(tree, node)
            for ancestor in ancestors:
                path_from_source.append(ancestor) if node == node_source else path_from_target.append(ancestor)
                if ancestor == common_ancestor:
                    break

    # path_from_target is reversed to keep the sequence order:
    # source -> common ancestor  and common ancestor -> target
    path_from_target = path_from_target[::-1]
    # The last element in path_from_source is the same as the first element in path_from_target (the common ancestor).
    # We keep only one.
    path = path_from_source + path_from_target[1:]
    # print("node_source: ",node_source,"\nnode_target: ",node_target,"\ncommon_ancestor: ",common_ancestor,"\npath: ",path)
    return (path)


def findAncestors(tree, node):
    """
    Return the list of ancestors of a node.

    Args:
        tree (tlp.Graph):  A graph object.
        node (tlp.node): A node.

    Returns:
        ancestors (list): a list of nodes in the path from the node to the root
    """
    ancestors = []
    ancestor = node
    while ancestor != None:
        try:
            ancestor = tree.getInNode(ancestor, 1)
            ancestors.append(ancestor)
        except:
            ancestor = None
            return ancestors
    return ancestors


def findCommonAncestor(tree, node1, node2):
    """
    Find the nearest common ancestor of two nodes in a tree.

    Args:
        tree (tlp.Graph):  A graph object
        node1 (tlp.node): A node.
        node2 (tlp.node): An other node.
    Returns:
        node (tlp.node): A node if it found a common ancestor or None if there is no common ancestor
    """
    node1_ancestors = findAncestors(tree, node1)
    node2_ancestors = findAncestors(tree, node2)

    # we need to check if one node in parameter is the root of the tree (don't have any ancestor).
    if node1_ancestors == []:
        return node1
    elif node2_ancestors == []:
        return node2

    for ancestor_1 in node1_ancestors:
        for ancestor_2 in node2_ancestors:
            if ancestor_1 == ancestor_2:
                return ancestor_1
            elif ancestor_1 == node2:  # if the ancestor of node1 is node2
                return node2
            elif ancestor_2 == node1:  # if the ancestor of node2 is node1
                return node1
    return None


def makeEdgesBundlesFromTree(tree, graph, layout):
    """
    Curve the edges, by taking as control points the vertices of a tree present in the path connecting the two nodes of each edge.

    Args:
        tree (tlp.Graph): A hierarchical tree
        graph (tlp.Graph): The graph whose edges are curved
        layout (tlp.LayoutProperty): The layout holding the coordinates of nodes & edges
    """
    graph.getIntegerProperty("viewShape").setAllEdgeValue(tlp.EdgeShape.CubicBSplineCurve)
    for edge in graph.getEdges():
        node_src = graph.source(edge)
        node_tgt = graph.target(edge)
        path = findShortestPathTree(tree, node_src, node_tgt)
        coord_list = []
        for node in path:
            coord_list.append(layout.getNodeValue(node))
        layout[edge] = coord_list


def generateSmallMultiples(graph, mode_relative):
    """
    Generate subgraph/views of a graph for each double property of the graph in the format "tp[number]_s". It's used for generating graph associated to timestamps.

    Args:
        graph (tlp.Graph): A graph containing double properties in the format "tp[number]_s"
        mode_relative (boolean): If True, each value for a time property will be relative to it's basal level. In this function the basal level is calculated as the median of the first 5 timestamps for a particular node. For each node this median is substracted to the absolute value. If mode_relative is set to False, the absolute value is kept. It's particularly interesting to use relative value in order to see local changes of expression at different level.

    Returns:
        small_multiple (tlp.Graph): the new graph created,
        min_value (int): minimum value found in all the double properties matching the described format,
        max_value (int): maximum value found in all the double properties matching the described format
    """
    small_multiple = graph.getSuperGraph().addSubGraph(selection=None, name="Small Multiples")
    print("Please wait while small multiples are generated. This may take a moment depending on the machine...")
    time_properties = findTimeProperty(graph)

    min_value = 0
    max_value = 0
    for propty in time_properties:
        subgraph = small_multiple.addSubGraph(name=propty)
        tlp.copyToGraph(subgraph, graph)
        viewMetric_local = subgraph.getLocalDoubleProperty("viewMetric")
        propty_value = subgraph.getDoubleProperty(propty)

        for node in subgraph.getNodes():
            if mode_relative:
                time_values = []
                for propty2 in time_properties[0:5]:
                    time_propty_temp = subgraph.getDoubleProperty(propty2)
                    time_values.append(time_propty_temp[node])
                median = statistics.median(time_values)
                viewMetric_local[node] = propty_value[node] - median
            else:
                viewMetric_local[node] = propty_value[node]
            min_value = viewMetric_local[node] if viewMetric_local[node] < min_value else min_value
            max_value = viewMetric_local[node] if viewMetric_local[node] > max_value else max_value

    print("Done !")
    return small_multiple, min_value, max_value


def findTimeProperty(graph):
    """
    Find all timestamp property in the graph (with the format: tp[number] s)

    Args:
        graph (tlp.Graph): A graph object
    Returns:
        propty_list (list): a sorted list containing strings for each timestamp property
    """
    string_property_list = graph.getProperties()
    propty_list = []
    for propty in string_property_list:
        pattern = re.compile("tp\d+ s")  # find property with the format: tp[number] s
        if pattern.match(propty):
            propty_list.append(propty)

    # sort this list in the right order (t1s, t10s, t2s --> t1s, t2s, t10s)
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(propty_list, key=alphanum_key)


def setSmallMultiplesColor(smallMultiples_graph, min_value, max_value):
    """
    Set color of each node for all the subgraph in small multiples.

    Args:
        smallMultiples_graph (tlp.Graph): small mutliple graph
        min_value (int): minimum value for the color gradient
        max_value (int): maximum value for the color gradient
    """
    for subgraph in smallMultiples_graph.getSubGraphs():
        viewMetric_local = subgraph.getLocalDoubleProperty("viewMetric")
        colorByProperty(subgraph, viewMetric_local, localColor=False, min_propty_value=min_value,
                        max_propty_value=max_value)


def subgraphGrid(graph, nbcolumn):
    """
    Align all the subgraph of a graph, in a grid.

    Args:
        graph (tlp.Graph): A parent graph
        nbcolumn (int): number of column in the grid
    """
    # get one subgraph's bounding box
    boundingBox = tlp.computeBoundingBox(graph.getNthSubGraph(1))
    number_of_visited_subgraph = 0
    size_X = 2.5 * abs(
        boundingBox[1][0] - boundingBox[0][0])  # we multiply by 2.5 (2*radius + 0.5 to have a small padding)
    size_Y = 2.5 * abs(
        boundingBox[1][1] - boundingBox[0][1])  # we multiply by 2.5 (2*radius + 0.5 to have a small padding)
    offset_X = number_of_visited_subgraph * size_X
    offset_Y = number_of_visited_subgraph * size_Y
    layout = graph.getLayoutProperty("viewLayout")
    for subgraph in graph.getSubGraphs():
        number_of_visited_subgraph += 1
        for node in subgraph.getNodes():
            layout[node] += layout[node] + tlp.Vec3f(offset_X, -offset_Y, 0)
        for edge in subgraph.getEdges():
            control_points = layout[edge]
            new_control_points = []
            for vector in control_points:
                new_control_points.append(tuple(map(sum, zip(vector, (offset_X, -offset_Y, 0)))))
            layout[edge] = new_control_points
        offset_X = number_of_visited_subgraph % nbcolumn * size_X
        offset_Y = (number_of_visited_subgraph // nbcolumn) * size_Y


def generateAndComputeMultiples(graph_source, nbcolumn, mode_relative):
    """
    Generate subgraph/views of a graph for each double property of the graph in the format "tp[number]_s". It's used for generating graph associated to timestamps. It also set the color of each node based on it's value and align it in a grid in the parent graph.

    Args:
        graph_source (tlp.Graph): A graph containing double properties in the format "tp[number]_s".
        graph_source (int): Number of column in the grid.
        mode_relative (boolean): If True, each value for a time property will be relative to it's basal level. In this function the basal level is calculated as the median of the first 5 timestamps for a particular node. For each node this median is substracted to the absolute value. If mode_relative is set to False, the absolute value is kept. It's particularly interesting to use relative value in order to see local changes of expression at different level.
    Returns:
        smallmultiples (tlp.Graph): The graph generated.
    """
    smallmultiples, min_value, max_value = generateSmallMultiples(graph_source, mode_relative)
    setSmallMultiplesColor(smallmultiples, min_value, max_value)
    subgraphGrid(smallmultiples, nbcolumn)
    return smallmultiples


def pointsOnCircle(center, radius, n):
    """
    Generate N points on a circle.
    Args:
        center (tuple): Coordinates (x,y) of the center of the circle as a tuple.
        radius (int): Length of the radius.
        n (int): Number of point on the circle.
    Returns:
        Liste_coordinates (list): List of all point's coordinates.
    """
    return [(center[0] + (math.cos(2 * pi / n * x) * radius), center[1] + (math.sin(2 * pi / n * x) * radius)) for x in
            range(0, n + 1)]


def longestPathWithNode(list_of_paths, node):
    """
    Find in a list of path the longest one with a specific node and return the length of this path

    Args:
        list_of_paths (list): List of path
        node (tlp.node): A specific node searched in each path.
    Returns:
        longest_path (list): Longest path with the searched node.
    """
    max_length_of_path = 0
    longest_path = list_of_paths[0]  # initialize with the first one
    for path in list_of_paths:
        if node in path and len(path) > max_length_of_path:
            max_length_of_path = len(path)
            longest_path = path
    # print("node:", node,"path: ", longest_path, "length:", max_length_of_path)
    return longest_path


def findLeftAndRightLeaf(tree, node):
    """
    Search in a subtree for the leftmost leaf and the rightmost leaf with a specified node as root.
    Args:
        tree (tlp.graph): A tree where each leaf are searched.
        node (tlp.node): The root of the subtree, it can be any node of the tree.
    Returns:
        left_leaf (tlp.node): Leftmost leaf of the subtree
         right_leaf (tlp.node): Rightmost leaf of the subtree
    """
    left_leaf = findLeftLeaf(tree, node)
    right_leaf = findRightLeaf(tree, node)
    return left_leaf, right_leaf


def findLeftLeaf(tree, node):
    """Find the leftmost leaf of a subtree with node as root"""
    currentnode = node
    while True:
        childs = []
        try:
            for child in tree.getOutNodes(currentnode):
                childs.append(node)
            currentnode = tree.getOutNode(currentnode, 1)
        except:
            return currentnode


def findRightLeaf(tree, node):
    """Find the rightmost leaf of a subtree with node as root"""
    currentnode = node
    while True:
        childs = []
        try:
            for child in tree.getOutNodes(currentnode):
                childs.append(node)
            currentnode = tree.getOutNode(currentnode, len(childs))
        except:
            return currentnode


def distanceBetweenTwoPoints(point1, point2):
    """Computes the distance between two points(x,y)"""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


def slopeEquationParameter(point1, point2):
    """Returns the slope of the line passing through two points(x,y)"""
    if (point2[0] - point1[0]) == 0:
        return "infinite slope"
    a = (point2[1] - point1[1]) / (point2[0] - point1[0])
    b = (point2[1] - (a * point2[0]))
    return a


def coordinateOnLineAtSpecifiedDistance(origin_point, slope, distance, pointReference):
    """
    Computes the coordinates of a point at a specified distance from origin point on a line with specified slope

    Args:
        origin_point (tuple): Coordinates (x,y) of the point of origin.
        slope (int): Slope of the line passing through the point of origin.
        distance (int): Distance from the point of origin.
        pointReference (tuple): Coordinates (x,y) of a point that allow to decide wich point from the solutions (up to 2) is near it and must be taken.

    Returns:
        point (tuple): Coordinate (x,y) of the point at specified distance from origin.
    """
    pointA = (0, 0)
    pointB = (0, 0)
    if slope == 0:
        pointA = (origin_point[0] + distance, origin_point[1])
        pointB = (origin_point[0] - distance, origin_point[1])

    elif slope == "infinite slope":
        pointA = (origin_point[0], origin_point[1] + distance)
        pointB = (origin_point[0], origin_point[1] - distance)

    else:
        dx = (distance / math.sqrt(1 + (slope * slope)))
        dy = slope * dx
        pointA = (origin_point[0] + dx, origin_point[1] + dy)
        pointB = (origin_point[0] - dx, origin_point[1] - dy)

    if distanceBetweenTwoPoints(pointReference, pointA) < distanceBetweenTwoPoints(pointReference, pointB):
        return pointA
    else:
        return pointB


def setTrueRadialLayout(tree, oneLevelRadius):
    """
    This function assign a true radial layout (all leafs are on a circle) on a graph.

    Args:
        tree (tlp.graph): The tree on which the layout will be applied
        oneLevelRadius (int): Length of one level in the graph hierarchy

    """
    # At first this function get the longest path, ie the max number of level in the hierarchy.
    # It will be the number of concentric circle in the tree
    longest_path_len = 0
    longest_path = []
    path_list = []
    numberOfLeaf = 0
    leaf_nodes = []
    layout = tree.getLayoutProperty("viewLayout")
    for node in tree.getNodes():
        path = [node] + findAncestors(tree, node)
        try:  # try to get the first descendant of the node, if an exception is returned, this is a leaf
            tree.getOutNode(node, 1)
        except:
            numberOfLeaf += 1
            leaf_nodes.append(node)
            path_list.append(path)
            if len(path) > longest_path_len:
                longest_path_len = len(path)
                longest_path = path

    # Get the root of the tree (center of the circle)
    root_tree = longest_path[-1]
    center = layout[root_tree]
    circleRadius = oneLevelRadius * (longest_path_len - 1)
    # Generate a list of coordinate on a circle with the root as center and edge length * the length of the longest past (without root) as radius
    coordinates = pointsOnCircle(center=(0, 0), radius=circleRadius, n=numberOfLeaf)

    # Assign each leaf on this circle
    for i in range(len(leaf_nodes)):
        layout[leaf_nodes[i]] = coordinates[i]

    # Now, each node parent of leafs will be placed between the middle of the chord (defined by the first child and the last child of the node) and the center (the root)

    for node in tree.getNodes():
        if node not in leaf_nodes and node != root_tree:
            longest_path_current_node = longestPathWithNode(path_list, node)
            left_leaf, right_leaf = findLeftAndRightLeaf(tree, node)
            number_of_ancestor = len(findAncestors(tree, node))
            middle_of_chord = (
                (layout[left_leaf][0] + layout[right_leaf][0]) / 2, (layout[left_leaf][1] + layout[right_leaf][1]) / 2)

            distance_from_center = circleRadius * (number_of_ancestor / (len(longest_path_current_node) - 1))
            coord_parent = tlp.Vec3f(
                coordinateOnLineAtSpecifiedDistance(center, slopeEquationParameter(center, middle_of_chord),
                                                    distance_from_center, middle_of_chord))
            layout[node] = coord_parent
        # print(first_descendant_coord,last_descendant_coord,middle_of_chord)


def main(graph):
    Negative = graph.getBooleanProperty("Negative")
    Positive = graph.getBooleanProperty("Positive")
    locus = graph.getStringProperty("locus")
    tp1_s = graph.getDoubleProperty("tp1 s")
    viewColor = graph.getColorProperty("viewColor")
    viewLabel = graph.getStringProperty("viewLabel")
    viewLabelPosition = graph.getIntegerProperty("viewLabelPosition")
    viewLayout = graph.getLayoutProperty("viewLayout")
    viewMetric = graph.getDoubleProperty("viewMetric")
    viewShape = graph.getIntegerProperty("viewShape")
    viewSize = graph.getSizeProperty("viewSize")
    graphInteractions = graph.getSubGraph("Genes interactions")

    # Question 4
    # Question 1.1
    # assignLabelFromPropty(graph, locus, viewLabel)
    # Question 1.2
    assignNodeSize(graph, viewSize, 5500)

    # Question 1.3
    viewLabelPosition.setAllNodeValue(0)
    setAllRegulationStyle(graph, Negative, Positive, localColor=False)

    # Question 1.4
    drawWithAlgo(graph, viewLayout, "FM^3 (OGDF)")

    # Question 2.1
    createclusterTree(graph, "Genes interactions")
    clusterTree = graph.getSubGraph("Cluster Hierarchy")

    # Question 2.2
    setRadialLayout(graph, viewLayout)

    # Question 2.3
    # colorByProperty(graph, tp1_s, localColor=True, minValue=None, maxValue=None)

    # Question 2.4
    makeEdgesBundlesFromTree(clusterTree, graphInteractions, viewLayout)

    # Question 3

    smallmultiples = generateAndComputeMultiples(graphInteractions, 6, False)

    # Question BONUS 1:
    setTrueRadialLayout(clusterTree, 100000)
    makeEdgesBundlesFromTree(clusterTree, graphInteractions, viewLayout)
    smallmultiples = generateAndComputeMultiples(graphInteractions, 6, True)
