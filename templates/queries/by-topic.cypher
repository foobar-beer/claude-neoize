// Pull every lesson on a theme. The way you used to scroll one big doc section, now by relevance.
// Replace $topic with the topic id, e.g. 'getting-started'. $products is the shared+project union, so a
// theme shows this project's lessons AND the universal (shared) ones. The MCP read tool binds it for you;
// in the Neo4j Browser set it once with  :param products => ['shared','yourproduct'].
MATCH (l:Lesson)-[:ANCHORS_TO]->(t:Topic {id: $topic})
WHERE l.product IN $products AND t.product IN $products AND l.status <> 'retired'
RETURN l.product AS space, l.title AS title, l.body AS body, l.prov_date AS learned
ORDER BY l.prov_date DESC;
