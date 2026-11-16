// What breaks if I touch this. Everything that depends, directly or transitively, on a node, plus the
// lessons anchored to any of them. Assumes the project's structural layer uses a DEPENDS_ON edge;
// rename it to whatever your collect.py emits. Replace $id with the structural node id. $product scopes
// to your product (the MCP tool binds it; in the Browser set :param product => 'yourproduct').
MATCH (target {product: $product, id: $id})
OPTIONAL MATCH (target)<-[:DEPENDS_ON*]-(dependent {product: $product})
WITH target, collect(DISTINCT dependent) AS dependents
UNWIND ([target] + dependents) AS n
OPTIONAL MATCH (l:Lesson {product: $product})-[:ANCHORS_TO]->(n) WHERE l.status <> 'retired'
RETURN n.id AS node, labels(n)[0] AS kind, collect(DISTINCT l.title) AS lessons
ORDER BY kind, node;
