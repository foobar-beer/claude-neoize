// Pull every lesson on a theme. The way you used to scroll one big doc section, now by relevance.
// Replace $topic with the topic id, e.g. 'getting-started'.
MATCH (l:Lesson)-[:ANCHORS_TO]->(:Topic {id: $topic})
WHERE l.status <> 'retired'
RETURN l.title AS title, l.body AS body, l.prov_date AS learned
ORDER BY l.prov_date DESC;
