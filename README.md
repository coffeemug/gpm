gpm
=

A nice way to query github issues for project management work.

```
gpm
> set token a8h
> set repo rethinkdb/rethinkdb
rethinkdb/rethinkdb> fetch
Fetched 480 issues, 8 new, 4 closed
rethinkdb/rethinkdb> list
  [#3] The very third issue ever
  [#4] The fourth issue
rethinkdb/rethinkdb> list --closed
  [#1] The very first issue ever
  [#2] The second issue
rethinkdb/rethinkdb> list --all
  [#1] The very first issue ever
  [#2] The second issue
  [#3] The very third issue ever
  [#4] The fourth issue
```
