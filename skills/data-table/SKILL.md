---
name: data-table
description: >
  data.table semantics and footguns: i/j scoping and column-name shadowing,
  joins, by-reference updates, keys and type coercion. Use when writing or
  reviewing data.table code, or when a filter/join/aggregate returns unexpected
  rows or silently mutates its input.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

# data.table semantics

## When to use

- Writing or reviewing `data.table` filters, joins, aggregations, or updates.
- A `DT[i]` expression returns too many/few rows, or a function mutates its
  caller's data.
- Choosing between `DT[...]`, `set*()`, and `copy()`.

For formatting/style (no piped `set*`, indentation) see the
`r-package-style-guide` skill.

## Scoping: columns shadow outer variables in `i`

Inside `DT[i]`, a bare name that matches a column is evaluated **as the column**,
even when the calling function has a variable of the same name. A filter can
silently compare a column with itself and match everything or nothing:

```r
f <- function(DT, row_hash) {
  # BUG: `row_hash` in i is the column, not the argument -> the filter is always
  # false and every existing row is dropped (this emptied the override file
  # on every write, keeping only the newest entry).
  DT[which(DT$row_hash != row_hash)]
}
```

Fix by renaming the local, or parameterise explicitly with `env`:

```r
target <- row_hash
DT[which(DT$row_hash != target)]

DT[which(row_hash != target), env = list(target = row_hash)]
```

The same shadowing applies to `==`, `%in%`, arithmetic, and `j` expressions.
`..var` (or `get("var")`) forces an outer variable in `j`. `$` and `[[` are
always explicit: `DT[["row_hash"]]` is the column even if a local has that name.

**Testing:** cover filters with a same-named local — that is the regression that
catches this class of bug.

## By-reference updates

- `:=`, `set*()`, and `setDT()` mutate in place. Callers see the change; a
  function that should not mutate must `copy()` first (deep copy, costs memory).
- Do not pipe `set*()` functions (see the style guide).
- `DT[, new := ...]` adds by reference; `DT$new <- ...` also mutates a
  `data.table` (it is not a base data.frame copy) — prefer `:=`.
- `rbindlist(list(...), fill = TRUE)` when members have different columns;
  without `fill` the extra columns are dropped.

## Joins

- `X[Y, on = c("a" = "b")]` is a left join of `Y`'s rows onto `X`.
- Column collisions from `i` are prefixed `i.`; use it explicitly instead of
  relying on name resolution.
- `nomatch = NULL` is an inner join; `!Y` is an anti-join; `which = TRUE` returns
  row positions for a lookup.
- `mult = "first"`/`"last"` when the `i` key is not unique and only one match is
  wanted — otherwise the result silently multiplies rows.
- Join keys must have compatible types: `integer` vs `double` and `factor` vs
  `character` keys join by coercion and can surprise; cast explicitly.

## Aggregation

- `by =` groups; `.N` counts, `.SD` is the row subset, `.GRP` the group index.
- `keyby =` sorts the result and sets the key; plain `by` does not guarantee
  order.
- Aggregate functions must return a scalar per group or a list column — a
  length-mismatch error usually means the function leaks the whole vector.

## Keys and ordering

- `setkey()`/`keyby` sort by reference and enable fast joins; `setorder()` sorts
  without setting a key.
- `DT[order(-date)]` copies; `setorder(DT, -date)` mutates. Pick deliberately.

## Common footguns

- `DT[which(...)]` works but a bare logical `DT[...]` is enough; `which()` is
  only needed for row positions.
- `%in%` against `NA` matches nothing; add `| is.na(x)` deliberately when open
  rows are part of the population.
- `unique()`/`duplicated()` on a `data.table` with list columns behaves on the
  whole row; use explicit keys when de-duplicating by id.
