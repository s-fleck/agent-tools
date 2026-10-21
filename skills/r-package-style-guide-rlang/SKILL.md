---
name: r-package-style-guide-rlang
description: Use together with the r-package-style-guide skill when the package depends on rlang — overrides the base error rules with rlang::abort(..., call = NULL), keeps condition classes on rethrow via cnd_signal(), and adds parent conditions for extra context. Not for base-R-only packages.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

# R package style guide — rlang overlay

Error rules for R packages that depend on **rlang**. Every other rule in the
style guide — pipes, formatter, prohibited packages, data.table, file and
console I/O, database access — stays exactly as `r-package-style-guide` says.

## When To Use

- The package's `DESCRIPTION` imports or depends on rlang.
- The style guide's error rules are being applied to rlang code.
- **Not** for base-R-only packages: they follow the base rules unchanged.

## Load it with the base guide

Use `r-package-style-guide` for the shared rules. This skill overrides the
"Errors (fail loud)" section and nothing else. If the package has no rlang
dependency, apply nothing from here.

## Overrides — Errors (fail loud)

- **Error primitive is `rlang::abort(..., call = NULL)`** — `call = NULL`
  suppresses the call site in the message. `stop()` is banned in package code.
- **`abort()`'s second positional argument is `class`** — never pass a second
  unnamed string (it becomes the condition class and can recurse to a stack
  overflow; this bit a split message in a real package). Combine message parts
  with `sprintf()`/`paste0()` into one string.
- **Rethrow preserves the original condition**: inside `tryCatch(..., error = ...)`
  log with context, then `rlang::cnd_signal(e)` — never `stop(e)` or `abort()`,
  which lose the original class and call.
- **Add context with a parent, not a replacement**: `rlang::abort(message,
  parent = e)` keeps the original condition in the chain, so the caller still
  sees the cause.
- **Assertions**: rlang ships no assertion helper. Use the project's vendored
  one if it has one, otherwise validate explicitly and raise with `abort()`. The
  base guide's NA-safe predicate rules still apply.

## Red Flags — Stop And Reconsider

- `stop()` in package code where `abort()` is available.
- `abort("message", "class")` — a second unnamed string becomes the class.
- Re-raising with `stop(e)` or a fresh `abort()` instead of `cnd_signal(e)`.
- `rlang::abort()` in a package that does not depend on rlang.
