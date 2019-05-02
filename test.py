from py2neo import *

graph = Graph("bolt://3.84.239.221:33521", auth=("neo4j", "alphabet-malfunctions-sap"))

results = graph.match(r_type="ACTED_IN")
# results = graph.run("Match (n)-[b]-(a) return labels(n),n.name,n.title,b,a").to_table()
#
# for rel in results.nodes:
#     print(rel)

print(results)
for rel in results:
    print(rel)


