# dbt test

## Description  
`dbt test` **executes assertions against your data** to validate business logic and data quality.  
It runs two categories of tests:

| Test Type        | Defined On | Purpose                                                       |
|------------------|------------|---------------------------------------------------------------|
| **Schema / Data**| Models, sources, snapshots, seeds | Validate column constraints (e.g. `unique`, `not_null`, `accepted_values`) and _generic_ integrity rules. |
| **Unit**         | SQL models | Assert the behaviour of custom business logic in *unit-test* YAML files. |

A successful run returns **zero failures**. Any failure sets a non-zero exit-code, making `dbt test` CI-friendly.

---

## Arguments  

| Name        | Required | Description |
|-------------|----------|-------------|
| `selector`  | No (string) | dbt selection syntax to limit which tests run (see examples). |

---

## Usage Guidelines  

### ✅ DO
* Use **selectors** to run only the tests relevant to your change set—speeds up feedback loops.
* Pair `state:modified` with CI pipelines to test resources changed by the current commit.
* Keep tests close to logic: schema tests in the same YAML as models; unit tests alongside SQL.

### ❌ DON’T
* Rely solely on data tests for pipeline integrity—complement with `dbt build` in production.
* Ignore failures in CI; treat any regression as a blocker before merge.

---

## Examples  

### 1. Run **all** tests in the project  
```bash
dbt test
```

### 2. Run tests for a single staging model only  
```bash
dbt test --select stg_orders
```

### 3. CI optimisation – test only modified resources  
```bash
dbt test --select state:modified
```

### 4. Test a model **and** its downstream dependants  
```bash
dbt test --select stg_customers+
```

### 5. Validate unit tests only (by folder pattern)  
```bash
dbt test --select fqn:*unit_tests*
```

---

## Related Commands  

* **`dbt build`** – Superset that runs models _and_ downstream tests / snapshots / seeds.  
* **`dbt run`** – Materialise models before testing (data tests do not execute here).  
* **`dbt compile`** – Validate SQL/Jinja separately before running tests.
