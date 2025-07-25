# dbt build

## Description  
`dbt build` is the “all-in-one” command for _productionising_ a dbt project.  
It executes **all downstream actions** necessary to fully materialise the DAG:

| Action | What it does | Notes |
|--------|--------------|-------|
| **run**      | Executes SQL for models and materialises them (table / view / incremental) | Always adheres to model materialisation strategy |
| **test**     | Runs _data tests_ (`tests/`) and _schema tests_ (`yml`) against the newly-built relations | Fails the invocation if any test fails |
| **snapshot** | Executes snapshot queries and updates snapshot tables | Only executed when snapshots exist / are selected |
| **seed**     | Loads CSV seed files into the warehouse | Skipped when no seeds are selected |

Tasks are executed **in DAG order**, so dependencies are always honoured.

---

## Arguments  

| Name | Required | Description |
|------|----------|-------------|
| `selector` | No (string) | Graph selector that limits what part of the DAG to build. Strongly recommended for large projects. See examples below for syntax. |

_All standard dbt flags (`--profiles-dir`, `--vars`, `--threads`, etc.) declared in `profiles.yml` are respected automatically by the underlying CLI._

---

## Usage Guidelines  

### ✅ DO
* Use a **selector** whenever possible to avoid unnecessarily rebuilding the entire DAG.
* Build **+model_name** when you want to regenerate a model _and_ its children (tests, snapshots, downstream marts, etc.).
* Use `model_name+` sparingly; it can trigger an expensive full-DAG rebuild.
* In CI pipelines, prefer `dbt build --select state:modified+` to build only items modified by the current commit.

### ❌ DON’T
* Combine `--select` _and_ `--exclude` in ways that leave orphaned tests; they will still execute.
* Expect `dbt build` to skip tests—**tests always run** for selected nodes.

---

## Examples  

### 1. Build everything
```bash
dbt build
```

### 2. Build a single model and everything downstream
```bash
dbt build --select my_model+
```

### 3. Build a model _and_ its parents (useful for local debugging)
```bash
dbt build --select +my_model
```

### 4. CI / PR build: only modified resources
```bash
dbt build --select state:modified+
```

### 5. Target only marts
```bash
dbt build --select fqn:*marts*
```

---

## Related Commands  
* **`dbt run`** – Only materialise models (no tests / snapshots / seeds).  
* **`dbt test`** – Run tests only.  
* **`dbt compile`** – Generate SQL without executing it.
