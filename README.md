gpm
=

A nice way to query github issues for project management work.

```
# Get all open issues assigned to mlucy with labels `reql` and `high`
gpm --owner mlucy --labels reql,high

# Could be issued as
gpm -o mlucy -l reql,high

# Explicitly provide token and repo (these are cached, so we don't
# have to type them every time)
gpm --token a8b --repo rethinkdb/rethinkdb --owner mlucy --labels reql,high --open
```
