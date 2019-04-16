from py2neo import Graph

graph = Graph(auth=("neo4j", "1234"))
results = graph.run("match (a:Person) return a.name")
for result in results:
    print(result['a.name'])