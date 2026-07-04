# sample_data — synthetic internal knowledge

Everything under this directory is **fictitious and synthetic**. It models the internal knowledge of a
make-believe company, **Meridian Logistics**, so the [`rag`](../rag) and [`mcp`](../mcp) layers have
realistic material to index and serve. None of it represents any real organization, system, or event.

```
sample_data/
├── services/orders-api/   # a fictional Python microservice (codebase context)
├── runbooks/              # on-call / operational runbooks
├── incidents/             # post-incident reports
└── architecture/          # system overview + ADRs
```

Why this shape: the target role's MCP servers expose "codebases, runbooks, incident history, and
architecture docs." These four folders mirror exactly those four context types.
