// Pull the lessons for a decision point (git-push, release, close-ticket...). This is what the
// PreToolUse hook runs the moment the operation fires. Replace $op with the operation id.
MATCH (l:Lesson)-[:ANCHORS_TO]->(:Operation {id: $op})
WHERE l.status <> 'retired'
RETURN l.title AS title, l.body AS body
ORDER BY l.title;
