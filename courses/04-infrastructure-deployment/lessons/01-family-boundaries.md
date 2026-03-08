# Lesson 01 - Family Boundaries

Sonic fits into a repo family. It should not absorb every responsibility.

Current split:

- `uDOS` owns shared architecture language and broader family coordination
- `uDOS-sonic` owns deployment and hardware bootstrap
- `uHOME-server` owns canonical `uHOME` runtime and install contracts

Sonic's job is:

`take reviewed deployment intent -> materialize it on hardware`

That means Sonic can stage or hand off `uHOME` work, but it must not redefine
the `uHOME-server` contract locally.
