// Pull the lessons for a decision point (git-push, release, close-ticket...). This is what the
// PreToolUse hook runs the moment the operation fires. Replace $op with the operation id. $product
// scopes to your product (the hook and the MCP tool bind it; in the Browser set :param product => '...').
MATCH (l:Lesson {product: $product})-[:ANCHORS_TO]->(:Operation {product: $product, id: $op})
WHERE l.status <> 'retired'
RETURN l.title AS title, l.body AS body
ORDER BY l.title;
