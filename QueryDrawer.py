# This file is part of Tulip (http://tulip.labri.fr)
#
# Authors: David Auber and the Tulip development Team
# from LaBRI, University of Bordeaux
#
# Tulip is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# Tulip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# That plugin imports a graph from a file in the GraphML format
# (see http://graphml.graphdrawing.org/)

import xml.sax

import tulipplugins
from py2neo import *
from tulip import *

# map GraphML node id to Tulip node
idToNode = {}


# Connexion à la base de donnée neo4j
# load = Graph("bolt://localhost:7687",auth=("neo4j","aaa"))

# Création du fichier graphml
# load.run("CALL apoc.export.graphml.query('MATCH p=()-[r:ACTED_IN]->() RETURN p LIMIT 50','C:/Users/jeanc/Desktop/Projet_Neomics/graph1.graphml',{useTypes:true, storeNodeIds:true})")

# XML Sax Content Handler for parsing GraphML files
class TulipGraphMLHandler(xml.sax.ContentHandler):

    def __init__(self, graph, file_path, uri, id, password):
        xml.sax.ContentHandler.__init__(self)
        self.graph = graph
        self.viewLayout = graph.getLayoutProperty('viewLayout')
        self.viewSize = graph.getSizeProperty('viewSize')
        self.viewColor = graph.getColorProperty('viewColor')
        self.viewLabel = graph.getStringProperty('viewLabel')
        self.attributes = {}
        self.currentNode = None
        self.currentEdge = None
        self.currentAttrId = None
        self.parsingDefault = False

    # try to create a Tulip property based on GraphML attribute type
    def getGraphProperty(self, attrId, attrName, attrType):
        if attrType == 'string':
            return self.graph.getStringProperty(attrName)
        elif attrType == 'boolean':
            return self.graph.getBooleanProperty(attrName)
        elif attrType == 'int' or attrType == 'long':
            return self.graph.getIntegerProperty(attrName)
        elif attrType == 'double' or attrType == 'float':
            return self.graph.getDoubleProperty(attrName)
        else:
            return None

    def startElement(self, name, attrs):
        # attribute definition
        if name == 'key':
            # only parse standarly defined attributes
            if 'attr.name' in attrs and 'attr.type' in attrs and 'for' in attrs:
                # save attributes info for later use
                self.attributes[attrs['id']] = {'name'    : attrs['attr.name'],
                                                'typename': attrs['attr.type'],
                                                'for'     : attrs['for']}
                self.currentAttrId = attrs['id']

        # attribute default value
        elif name == 'default':
            self.parsingDefault = True

        # node definition
        elif name == 'node':
            # get node id
            nodeId = attrs['id']
            # create a Tulip node
            n = self.graph.addNode()
            # map id to node
            idToNode[nodeId] = n
            # set the id as the default node label
            self.graph['viewLabel'][n] = nodeId
            # mark current node
            self.currentNode = n
            self.viewColor[n] = tlp.Color(162, 162, 162)
            if "Gene" in attrs['labels']:
                self.viewColor[n] = tlp.Color(212, 23, 23)
            if "GOI" in attrs['labels']:
                self.viewColor[n] = tlp.Color(56, 187, 61)
            if "Protein" in attrs['labels']:
                self.viewColor[n] = tlp.Color(212, 159, 23)
            if "Group" in attrs['labels']:
                self.viewColor[n] = tlp.Color(237, 16, 175)
            if "Tissue" in attrs['labels']:
                self.viewColor[n] = tlp.Color(197, 23, 212)
            if "Analysis" in attrs['labels']:
                self.viewColor[n] = tlp.Color(23, 144, 212)
            if "Experience" in attrs['labels']:
                self.viewColor[n] = tlp.Color(212, 114, 23)
            if "TF" in attrs['labels']:
                self.viewColor[n] = tlp.Color(23, 190, 212)


        # edge definition
        elif name == 'edge':
            # get source and target node id
            sourceId = attrs['source']
            targetId = attrs['target']
            # add the edge if the ids are valid and mark it as current
            if sourceId in idToNode and targetId in idToNode:
                self.currentEdge = self.graph.addEdge(idToNode[sourceId], idToNode[targetId])

        # attribute definition
        elif name == 'data':
            # if it is a standard one, mark it as current
            if attrs['key'] in self.attributes:
                self.currentAttrId = attrs['key']

    # reset current element parsed
    def endElement(self, name):
        if name == 'node':
            properties = self.graph.getNodePropertiesValues(self.currentNode)
            if properties.exist("name"):
                self.viewLabel[self.currentNode] = properties["name"]
            if properties.exist("id"):
                self.viewLabel[self.currentNode] = properties["id"]
            if properties.exist("family"):
                self.viewLabel[self.currentNode] = properties["family"]
            self.currentNode = None
        elif name == 'edge':
            self.currentEdge = None
        elif name == 'data' or name == 'key':
            self.currentAttrId = None
        elif name == 'default':
            self.parsingDefault = False

    # parse attributes values
    def characters(self, content):
        # nothing to parse
        if content == '\n':
            return

        # parsing attribute default value
        if self.currentAttrId:
            # get the name and the typename of the attribute
            attrName = self.attributes[self.currentAttrId]['name']
            attrType = self.attributes[self.currentAttrId]['typename']
            attrFor = self.attributes[self.currentAttrId]['for']

            if self.parsingDefault and (attrFor == 'node' or attrFor == 'edge'):
                # try to create a Tulip property compatible with the attribute type
                graphProperty = self.getGraphProperty(self.currentAttrId, attrName, attrType)
                if graphProperty:
                    if attrFor == 'node':
                        graphProperty.setAllNodeStringValue(content)
                    else:
                        graphProperty.setAllEdgeStringValue(content)

            # parsing attribute
            else:
                # parse node attribute
                if self.currentNode:
                    # try to parse some standard node visual attributes (label, layout, size, color)
                    if attrName == 'label':
                        self.viewLabel[self.currentNode] = content
                    elif attrName == 'x' or attrName == 'y':
                        nodeCoord = self.viewLayout[self.currentNode]
                        if attrName == 'x':
                            nodeCoord[0] = float(content)
                        else:
                            nodeCoord[1] = float(content)
                        self.viewLayout[self.currentNode] = nodeCoord
                    elif attrName == 'width' or attrName == 'height' or attrName == 'size':
                        nodeSize = self.viewSize[self.currentNode]
                        size = float(content)
                        if attrName == 'width' or attrName == 'size':
                            nodeSize[0] = size
                        if attrName == 'height' or attrName == 'size':
                            nodeSize[1] = size
                        self.viewSize[self.currentNode] = nodeSize
                    elif attrName == 'r' or attrName == 'g' or attrName == 'b':
                        nodeColor = self.viewColor[self.currentNode]
                        if attrName == 'r':
                            nodeColor[0] = int(content)
                        elif attrName == 'g':
                            nodeColor[1] = int(content)
                        else:
                            nodeColor[2] = int(content)
                        self.viewColor[self.currentNode] = nodeColor

                    # try to create a Tulip property compatible with the attribute type
                    graphProperty = self.getGraphProperty(self.currentAttrId, attrName, attrType)
                    if graphProperty:
                        # set the property value from its string representation
                        graphProperty.setNodeStringValue(self.currentNode, content)

                # same process for parsing edges attributes
                elif self.currentEdge:
                    graphProperty = self.getGraphProperty(self.currentAttrId, attrName, attrType)
                    if graphProperty:
                        graphProperty.setEdgeStringValue(self.currentEdge, content)

                # graph attribute case
                else:
                    self.graph.setAttribute(attrName, content)


class Import_graph(tlp.ImportModule):
    def __init__(self, context):
        tlp.ImportModule.__init__(self, context)
        self.addStringParameter("Query", help="Cypher Query to obtain sub-graph",
                                defaultValue="MATCH (a:GOI)-[b]-(c:Gene) return a,b,c",
                                isMandatory=True)
        self.addDirectoryParameter("Directory path", isMandatory=True, help="The path to the file")
        self.addStringParameter("File name", help="intermediate name of graphml", defaultValue="graph",
                                isMandatory=True)
        self.addStringParameter("URI", help="URI", defaultValue="bolt://localhost:7687", isMandatory=True)
        self.addStringParameter("User name", help="Neo4j DB user name", defaultValue="eliot", isMandatory=True)
        self.addStringParameter("Password", help="DB password", defaultValue="1234", isMandatory=True)

    def fileExtensions(self):
        return ["graphml"]

    def importGraph(self):
        load = Graph(self.dataSet["URI"], auth=(self.dataSet["User name"], self.dataSet["Password"]))

        # create an XML Sax parser
        parser = xml.sax.make_parser()
        # set our custom content handler
        file_path = self.dataSet["Directory path"] + "/" + self.dataSet["File name"] + ".graphml"
        load.run(
            "CALL apoc.export.graphml.query('{}','{}',{{useTypes:true, storeNodeIds:true}})".format(
                self.dataSet['Query'],
                file_path))

        parser.setContentHandler(
            TulipGraphMLHandler(self.graph, file_path, self.dataSet["URI"], self.dataSet["User name"],
                                self.dataSet["Password"]))
        # parse the GraphML file
        parser.parse(open(file_path, "rb"))
        
        params = tlp.getDefaultPluginParameters("FM^3 (OGDF)", self.graph)
        # get a reference to the default layout property
        viewLayout = self.graph.getLayoutProperty("viewLayout")
        
        # call the layout algorithm and store the result in viewLayout
        self.graph.applyLayoutAlgorithm("FM^3 (OGDF)", viewLayout, params)
        self.graph.applyAlgorithm("Edge bundling")
        viewShape = self.graph.getIntegerProperty("viewShape") 
        viewShape.setAllEdgeValue(tlp.EdgeShape.BezierCurve)
        return True


# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("Import_graph", "QueryDrawer", "Antoine Lambert, modifié par jc", "07/05/2019",
                                   """
                                   <p>Supported extension: graphml</p><p>Imports a graph from a file in the GraphML format (http://graphml.graphdrawing.org/).
                                   GraphML is a comprehensive and easy-to-use file format for graphs.
                                   It consists of a language core to describe the structural properties
                                   of a graph and a flexible extension mechanism to add application-specific data.</p>
                                   """, "1.0", "File")
