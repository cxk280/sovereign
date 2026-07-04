# Runbook: deploy & rollback (SYNTHETIC)

**Applies to:** all Fulfillment services, incl. orders-api · **CI/CD:** GitLab pipelines

## Deploy
- Merge to `main` triggers build → canary (10% traffic, 10m) → full rollout if golden signals hold.
- Migrations run **expand/contract**: additive migration ships and deploys before any code depends on
  it; destructive changes come in a later, separate migration.

## Rollback
1. `gitlab pipeline` → find the last green release; trigger the `rollback` job (redeploys the previous
   image tag). Rollback is image-only; it does **not** revert database migrations.
2. If a migration is implicated, roll back code first, then assess the migration separately — never
   drop columns to "undo" a deploy while old code may still read them.
3. Post in `#fulfillment-incidents`, open/annotate the incident, and page the DB on-call if data is
   involved.

## Guardrail
A rollback that would leave new code running against an un-migrated schema is unsafe. When in doubt,
hold traffic on the canary rather than completing the rollout.
