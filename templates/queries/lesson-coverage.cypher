// How the knowledge layer is distributed: lessons per topic and per operation, and anything with none.
// A topic with many lessons is a hot subsystem; an operation with zero is fine (the expected case).
MATCH (a)
WHERE a:Topic OR a:Operation
OPTIONAL MATCH (l:Lesson)-[:ANCHORS_TO]->(a) WHERE l.status <> 'retired'
RETURN labels(a)[0] AS kind, a.id AS id, count(l) AS lessons
ORDER BY lessons DESC, kind, id;
