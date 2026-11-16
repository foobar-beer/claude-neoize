// Pull every lesson on a theme. The way you used to scroll one big doc section, now by relevance.
// Replace $topic with the topic id, e.g. 'getting-started'. $product scopes to your product; the MCP
// read tool binds it for you, in the Neo4j Browser set it once with  :param product => 'yourproduct'.
MATCH (l:Lesson {product: $product})-[:ANCHORS_TO]->(:Topic {product: $product, id: $topic})
WHERE l.status <> 'retired'
RETURN l.title AS title, l.body AS body, l.prov_date AS learned
ORDER BY l.prov_date DESC;
