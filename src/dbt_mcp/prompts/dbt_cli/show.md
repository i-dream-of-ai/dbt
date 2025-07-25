# dbt show

## Description
`dbt show` lets you **preview data** without materialising anything in the warehouse.  
It can run either:

* **Inline SQL** provided via `--inline`, or  
* A **model / node selector** provided via `--select`

Typical use-cases include:

* Previewing rows from a model or source
* Testing intermediate CTE logic inside complex models
* Performing quick ad-hoc analyses without creating tables/views

Because the command simply returns a result set, it is fast and safe to run in development environments.

---

## Arguments

| Name        | Required | Description |
|-------------|----------|-------------|
| `sql_query` | One of\* | SQL to execute. Do **not** append a semicolon or `LIMIT` clause. |
| `selector`  | One of\* | dbt selection syntax (e.g. `stg_orders`, `+orders_mart+`, `fqn:*stg_*`). |
| `limit`     | No       | Maximum rows to return. If omitted the query is unbounded. Recommended default: **20-100** while exploring. |

\* Exactly **one** of `sql_query` *or* `selector` must be supplied. Supplying both (or neither) will result in an error.

---

## Usage Guidelines

### ✅ DO
* For SQL, use fully-qualified dbt references, e.g. `{{ ref('stg_orders') }}` or `{{ source('raw', 'payments') }}`.
* Wrap the SQL string in triple-quoted Python strings when calling the tool.
* Start with a reasonable `limit` while iterating, then remove/raise it once satisfied.
* Use selectors for quick previews of existing models without writing SQL.

### ❌ DON’T
* Pass **both** `sql_query` and `selector` together.
* Add a `LIMIT` clause inside `sql_query`; use the `limit` argument instead.
* Include a trailing semicolon—dbt adds this automatically.

---

## Examples

### 1. Preview first 25 rows of a staging model (SQL)
```python
sql_query = """
select *
from {{ ref('stg_orders') }}
"""
limit = 25
```

### 2. Preview a model using a selector (no SQL required)
```python
selector = "stg_orders"
limit = 25
```

### 3. Inspect an intermediate CTE in a model under development
```python
sql_query = """
with base as (
    select * from {{ ref('stg_payments') }}
),
filtered as (
    select * from base where status = 'completed'
)
select * from filtered
"""
limit = 20
```

### 4. Ad-hoc join of two marts to answer a quick business question
```python
sql_query = """
select
    o.order_id,
    o.order_total,
    c.customer_segment
from {{ ref('orders_mart') }} o
join {{ ref('customers_mart') }} c
    on o.customer_id = c.customer_id
where o.order_total > 100
"""
limit = 50
```

---

## Common Pitfalls & Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| `Must supply exactly one of --inline or --select` | Passed neither or both arguments | Provide only `sql_query` **or** `selector`. |
| `Query exceeds maximum result size` | No or very high `limit` | Lower the `limit` value. |
| `relation "…" does not exist` | Wrong target / schema | Verify `dbt debug` & target schema. |
| `Compilation Error` | Invalid Jinja in `sql_query` | Check templating & refs; run `dbt compile`. |

---

## Related Commands

* **`dbt compile`** – Validate SQL/Jinja without hitting the database.  
* **`dbt run`** – Materialise the results as a model after you’re satisfied with the query.  

For deeper details see the [official dbt docs on `dbt show`](https://docs.getdbt.com/reference/commands/show).
