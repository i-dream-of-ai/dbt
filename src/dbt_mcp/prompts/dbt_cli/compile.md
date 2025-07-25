# dbt compile

## Description
`dbt compile` renders the **executable SQL** for your dbt models, tests, and analyses, letting you catch Jinja or macro errors **before** any query hits the warehouse.

> **Best practice** – **Always** compile the SQL you plan to run or preview (e.g. with `dbt show`) so you fail fast on templating issues instead of during execution.

---

## Arguments

| Name        | Required | Description |
|-------------|----------|-------------|
| `sql_query` | One of\* | Inline SQL string to compile via `--inline`. |
| `selector`  | One of\* | dbt selection syntax (`stg_orders`, `+orders_mart+`, `fqn:*stg_*`, etc.) to compile via `--select`. |

\* Exactly **one** of `sql_query` *or* `selector` may be supplied. If both (or neither) are provided the tool returns an error. Omitting both compiles **the entire project**&nbsp;— useful in CI.

---

## Usage Guidelines

### ✅ DO
* Run `compile` every time you generate or edit SQL.
* Use **selector** when you want to compile a model or family of models without writing SQL.
* Use **sql_query** when you’ve built an ad-hoc query and need to validate its Jinja.

### ❌ DON’T
* Skip compilation and jump straight to `show`, `run`, etc. — you risk runtime failures.
* Provide both `sql_query` and `selector`; choose one.

---

## Examples

### 1. Compile a single model by selector
```python
compile(selector="stg_orders")   # MCP tool
```

### 2. Compile inline SQL
```python
sql_query = """
select * 
from {{ ref('stg_orders') }}
where order_total > 100
"""
compile(sql_query=sql_query)     # MCP tool
```

### 3. CI-style full-project compile
```python
compile()   # no args -> dbt compile whole project
```

### 4. End-to-end workflow with `dbt show`
```python
# 1️⃣ Validate the SQL renders
compile(sql_query=my_query)

# 2️⃣ Preview results once compile succeeds
show(sql_query=my_query, limit=25)
```

---

## Related Commands
* **`dbt show`** – Preview compiled SQL results.  
* **`dbt run`** – Materialise models after successful compilation.  
* **`dbt parse`** – Fast structural validation without full compilation.
