# dbt run

## Description  
`dbt run` **materialises models only**.  
For each selected model dbt:

1. Compiles the model’s SQL (including Jinja templating)  
2. Connects to the current target warehouse (as defined in `profiles.yml`)  
3. Executes the compiled SQL to create / update the relation according to its chosen _materialisation strategy_ (`table`, `view`, `incremental`, `ephemeral`, etc.)  

Models execute **in topological (DAG) order**, ensuring every upstream dependency is built before its children.

---

## Arguments  

| Name | Required | Description |
|------|----------|-------------|
| `selector` | No (string) | Graph selector expression to limit which models are run (see examples). |
| `full_refresh` | No (bool) | If `true`, incremental models are rebuilt from scratch with `INSERT … OVERWRITE`. |
| `threads` | No (int) | Override number of warehouse connections for this invocation. |

Additional dbt CLI flags (`--vars`, `--profiles-dir`, `--defer`, `--state`, etc.) are forwarded automatically when using this tool.

---

## Usage Guidelines  

### ✅ DO
* Use a **selector** whenever you need to run a subset of models—this saves time on large DAGs.
* Pair `state:modified` with CI workflows to run only models changed by the current commit.
* Set `--full-refresh` during back-fills or when changing incremental logic.

### ❌ DON’T
* Rely on `dbt run` for testing—no tests execute; follow up with `dbt test` or use `dbt build`.
* Forget that **ephemeral** models are _compiled_ but not materialised—they will not appear in the warehouse.

---

## Examples  

### 1. Run the entire project  
```bash
dbt run
```

### 2. Run a single model and its parents (staging rebuild)  
```bash
dbt run --select +stg_orders
```

### 3. Run all marts only  
```bash
dbt run --select fqn:*marts*
```

### 4. CI optimisation: run only models modified in this branch  
```bash
dbt run --select state:modified
```

### 5. Force-rebuild all incremental models  
```bash
dbt run --full-refresh
```

---

## Related Commands  

* **`dbt build`** – Superset that runs models _and_ downstream tests / snapshots / seeds.  
* **`dbt test`** – Execute data & schema tests only.  
* **`dbt compile`** – Generate compiled SQL without executing it.
