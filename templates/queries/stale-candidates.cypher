// Lessons that NAME a ticket or symbol you just changed, so you can reconcile the ones that describe
// now-fixed behaviour. The citation is only an upper bound: READ each one, never auto-retire.
// Replace $needle with the ticket id or symbol, e.g. 'VD-542' or 'MssqlConnectionPool'. $products is the
// shared+project union (the MCP tool binds it; in the Browser set :param products => ['shared','yourproduct']).
MATCH (l:Lesson)
WHERE l.product IN $products AND l.status = 'active' AND l.body CONTAINS $needle
RETURN l.product AS space, l.id AS id, l.title AS title, l.prov_date AS learned
ORDER BY l.prov_date;
