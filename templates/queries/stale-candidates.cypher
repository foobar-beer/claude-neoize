// Lessons that NAME a ticket or symbol you just changed, so you can reconcile the ones that describe
// now-fixed behaviour. The citation is only an upper bound: READ each one, never auto-retire.
// Replace $needle with the ticket id or symbol, e.g. 'VD-542' or 'MssqlConnectionPool'.
MATCH (l:Lesson)
WHERE l.status = 'active' AND l.body CONTAINS $needle
RETURN l.id AS id, l.title AS title, l.prov_date AS learned
ORDER BY l.prov_date;
