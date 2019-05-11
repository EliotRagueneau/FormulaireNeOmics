How to use Neomics :

Neomics are multiple plugins for Tulip software that can be use to import graph from neo4j and create a view of multiple graph comparison. Neomics are compose
by diferent python script call QueryMaker, QueryDrawer, AnalysisComparator and ScrollingFrame.

    -Installation requirement :

This is the list of software, plugins and library you need to use Neomics
1) Tulip : can be download on http://tulip.labri.fr/TulipDrupal/
2) Neo4j with apoc plugin : Neo4j can be download on https://neo4j.com/. Take neo4j-desktop, it's simpler to use and installation of apoc plugin.
3) Python version 3.5+ : can be download on https://www.python.org/.
4) One library for python have to be download : py2neo. You can use "pip install py2neo" command on bash to install it.


    -Folder :

This part explain where you have to put the diferent script. For this part you have two solutions.

first :
Put directly the script in the Tulip folders. If you do that, the plugins are automatically in Tulip when you launch the software.
1) Find the Tulip folder
2) QueryDrawer and QueryMaker in Tulip import plugin Python (/tulip/lib/tulip/python/tulip/plugins/import)
3) AnalysisComparator in Tulip general plugin python (/tulip/lib/tulip/python/tulip/plugins/general)
4) ScrollingFrame.py in the same folder than QueryDrawer and AnalysisComparator, so you have to duplicate it and put them in import and general

second :
Create a specific folder. If you do that, you have to load the diferents plugins script at every launch.
1) Create a folder "resources"
2) Put the different plugins on this folder : QueryMaker, QueryDrawer, AnalysisComparator and ScrollingFrame
3) Open the pythonIDE on Tulip and load the third plugin : QueryMaker, QueryDrawer and AnalysisComparator

    -Launch :

After installation and folder step you can find plugins :
1) In import plugin use QueryDrawer to import your subgraph corresponding of the query you create
2) In general Algorithm use AnalysisComparator to begin the comparaison of graph



Be free to use others plugins in Tulip for a better visualization
