gpm
=

A nice way to query github issues for project management work. I refer
to it as `gpm` (github product management) below, but you'd have to
create an alias to `main.py` (I'm too lazy to setup a proper
installer/packager).

```
# Specify a user/org, and repository to use
gpm -u rethinkdb -r rethinkdb

# Specify a github auth token (optional, but lets you fetch issues
# more often)
gpm -t a2c

# Fetch the issues from github
gpm --fetch

# Get all open issues owned by mlucy with labels `reql` and `high` in
# milestones 1.12 or 1.11.x
gpm -o mlucy -l reql high -m 12 -m x

# Get all open issues owned by mlucy or srh with labels `reql` and
# `high` in milestones 1.12 or 1.11.x
gpm -o mlucy -o srh -l reql high -m 12 -m x

# Get all open issues owned by mlucy or srh with labels `reql` and
# without the label `high` in milestones 1.12 or 1.11.x
gpm -o mlucy -o srh -l reql ~high -m 12 -m x

# Get all open issues owned by mlucy or srh with labels `reql` and
# without the label `high` in milestones 1.12 or 1.11.x and open them
# all in your web browser
gpm -o mlucy -o srh -l reql ~high -m 12 -m x -b
```
