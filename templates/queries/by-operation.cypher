// Pull the lessons for a decision point (git-push, release, close-ticket...). This is what the
// PreToolUse hook runs the moment the operation fires. Replace $op with the operation id. $products is
// the shared+project union, so an operation pulls its universal (shared) discipline AND this project's
// own. The hook and the MCP tool bind it; in the Browser set :param products => ['shared','yourproduct'].
MATCH (l:Lesson)-[:ANCHORS_TO]->(o:Operation {id: $op})
WHERE l.product IN $products AND o.product IN $products AND l.status <> 'retired'
RETURN l.product AS space, l.title AS title, l.body AS body
ORDER BY l.product, l.title;
