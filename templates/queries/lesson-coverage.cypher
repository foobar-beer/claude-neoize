// How the knowledge layer is distributed: lessons per topic and per operation across the shared+project
// union, plus anything with none. A topic with many lessons is a hot subsystem; an operation with zero is
// fine (the expected case). $products is the shared+project union (the MCP tool binds it; in the Browser
// set :param products => ['shared','yourproduct']). `space` tells you whether it is a shared or project node.
MATCH (a)
WHERE (a:Topic OR a:Operation) AND a.product IN $products
OPTIONAL MATCH (l:Lesson)-[:ANCHORS_TO]->(a) WHERE l.product IN $products AND l.status <> 'retired'
RETURN a.product AS space, labels(a)[0] AS kind, a.id AS id, count(l) AS lessons
ORDER BY lessons DESC, kind, id;
