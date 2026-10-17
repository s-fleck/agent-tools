#!/usr/bin/env Rscript
#
# check-docs.R — cross-reference checker for markdown documentation.
#
#   Rscript check-docs.R [path ...]
#
# Default (no arguments): every non-ignored *.md file (tracked and untracked),
# excluding
#   openspec/changes/**  (transient/archived working documents)
#   .opencode/**         (agent tooling, different conventions)
#   vendor dirs (.git, node_modules, renv, packrat, Rcheck)
# Pass explicit file/dir paths to check them regardless.
#
# Findings are printed as path:line: LEVEL: message; ERROR fails the run (exit 1):
#   ERROR  relative link/image targets exist; header Status lines carry `vX.Y (YYYY-MM-DD)`
#   ERROR  quoted `file.md § "heading"` references resolve from the named file
#   ERROR  file:line references exist and are in range
#   WARN   heading anchors and unquoted/numeric § references resolve
#   WARN   any missing target in files under openspec/changes/ (working docs may
#          legitimately reference not-yet-created files)
#
# Runs from the repo root; base R only.

args <- commandArgs(trailingOnly = TRUE)
default_mode <- !length(args)

paths <- if (!default_mode) {
  args
} else {
  git <- tryCatch(
    system2("git", c("ls-files", "-co", "--exclude-standard", shQuote("*.md")),
            stdout = TRUE, stderr = FALSE),
    error = function(e) character()
  )
  git <- git[file.exists(git) & !grepl("^(openspec/changes|\\.opencode)/", git)]
  if (length(git)) git else "."
}

files <- character()
for (p in paths) {
  if (dir.exists(p)) {
    f <- list.files(p, pattern = "\\.md$", recursive = TRUE, full.names = TRUE)
    f <- f[!grepl("(^|/)(\\.git|node_modules|renv|packrat)/|Rcheck/", f)]
    if (default_mode) f <- f[!grepl("(^|/)(openspec/changes|\\.opencode)/", f)]
    files <- c(files, f)
  } else if (file.exists(p)) {
    files <- c(files, p)
  } else {
    stop("no such path: ", p)
  }
}
files <- unique(normalizePath(files))

wd <- normalizePath(getwd())
rel <- function(p) if (startsWith(p, paste0(wd, "/"))) substring(p, nchar(wd) + 2L) else p

problems <- character()
add <- function(f, i, level, msg) {
  problems <<- c(problems, sprintf("%s:%d: %s: %s", rel(f), i, level, msg))
}

norm <- function(x) {
  x <- gsub("[^a-z0-9 ]", " ", tolower(x))
  gsub(" +", " ", trimws(x))
}
slug <- function(x) {
  x <- tolower(gsub("[`*~]", "", x))
  x <- gsub("[^a-z0-9 _-]", "", x)
  gsub(" +", "-", trimws(x))
}
headings_of <- function(lines) sub("^#{1,6} *", "", grep("^#{1,6} ", lines, value = TRUE))

doc <- lapply(files, function(f) readLines(f, warn = FALSE))
names(doc) <- files
heads <- lapply(doc, headings_of)
slugs <- lapply(heads, slug)

resolve <- function(target, from) {
  for (cand in c(file.path(dirname(from), target), target)) {
    if (file.exists(cand)) return(normalizePath(cand))
  }
  NA_character_
}
target_slugs <- function(tf) {
  if (tf %in% files) slugs[[tf]] else slug(headings_of(readLines(tf, warn = FALSE)))
}
matches_heading <- function(frag, h) {
  fn <- norm(frag)
  if (!nzchar(fn)) return(TRUE)
  for (hn in norm(h)) {
    if (grepl(fn, hn, fixed = TRUE) || grepl(hn, fn, fixed = TRUE)) return(TRUE)
  }
  FALSE
}

link_rx <- "\\[[^][]*\\]\\(([^()[:space:]]+)\\)"
fl_rx <- "([A-Za-z0-9_][A-Za-z0-9_./-]*\\.(R|r|Rmd|rmd|md|qmd|ya?ml|json|toml|sh|csv)):([0-9]+)(-([0-9]+))?"
status_rx <- "^\\s*\\**Status:\\**"
version_rx <- "v[0-9]+(\\.[0-9]+)+ \\([0-9]{4}-[0-9]{2}-[0-9]{2}\\)"

for (f in files) {
  lines <- doc[[f]]
  miss <- if (grepl("(^|/)openspec/changes/", f)) "WARN" else "ERROR"
  for (i in seq_along(lines)) {
    line <- lines[[i]]

    # relative links / images
    ms <- regmatches(line, gregexpr(link_rx, line))[[1]]
    for (t in sub("^.*\\((.*)\\)$", "\\1", ms)) {
      if (grepl("^(https?|mailto|ftp):", t)) next
      hash <- regexpr("#", t, fixed = TRUE)
      path <- if (hash > 0L) substr(t, 1L, hash - 1L) else t
      anchor <- if (hash > 0L) substring(t, hash + 1L) else ""
      tf <- if (nzchar(path)) resolve(path, f) else f
      if (is.na(tf)) {
        add(f, i, miss, sprintf("link target not found: %s", path))
        next
      }
      if (nzchar(anchor) && grepl("\\.md$", tf) && !tolower(anchor) %in% target_slugs(tf)) {
        add(f, i, "WARN", sprintf("heading anchor not found: %s#%s", path, anchor))
      }
    }

    # file:line references
    gm <- gregexpr(fl_rx, line)[[1]]
    if (gm[1L] > 0L) for (k in seq_along(gm)) {
      mstr <- substr(line, gm[[k]], gm[[k]] + attr(gm, "match.length")[[k]] - 1L)
      pre <- substr(line, max(1L, gm[[k]] - 10L), gm[[k]] - 1L)
      if (grepl("://", pre)) next
      tok <- sub(fl_rx, "\\1", mstr)
      l1 <- as.integer(sub(fl_rx, "\\3", mstr))
      l2 <- sub(fl_rx, "\\5", mstr)
      tf <- resolve(tok, f)
      if (is.na(tf)) {
        add(f, i, miss, sprintf("file reference not found: %s", mstr))
        next
      }
      n <- length(readLines(tf, warn = FALSE))
      if (l1 < 1L || l1 > n || (nzchar(l2) && !is.na(as.integer(l2)) && as.integer(l2) > n)) {
        add(f, i, miss, sprintf("line out of range (%d lines): %s", n, mstr))
      }
    }

    # section references
    sx <- gregexpr("\u00a7", line, fixed = TRUE)[[1]]
    if (sx[1L] > 0L) for (p in sx) {
      pre <- substr(line, max(1L, p - 80L), p - 1L)
      post <- substring(line, p + 1L)
      if (!nzchar(trimws(post))) next
      if (grepl("^`", post) || grepl("^s(\\b|\\s|'|$)", post)) next # `§` meta / "§s"
      qpat <- "^\\s*[\"'\u201c\u2018]([^\"'\u201c\u201d\u2018\u2019\\n]+)[\"'\u201d\u2019]"
      qm <- regmatches(post, regexpr(qpat, post))
      if (length(qm)) {
        frag <- sub(qpat, "\\1", qm)
        quoted <- TRUE
      } else {
        um <- regmatches(post, regexpr("^\\s+([^,;.)(\\n]{2,80})", post))
        if (!length(um)) next
        frag <- gsub("`", "", trimws(um))
        quoted <- FALSE
      }
      refs <- regmatches(pre, gregexpr("[A-Za-z0-9_./-]+\\.md", pre))[[1]]
      if (!length(refs)) {
        near <- substr(post, 1L, 60L)
        refs <- regmatches(near, gregexpr("[A-Za-z0-9_./-]+\\.md", near))[[1]]
      }
      tf <- if (length(refs)) resolve(refs[[length(refs)]], f) else f
      if (is.na(tf)) {
        add(f, i, miss, sprintf("section reference to missing file: %s", refs[[length(refs)]]))
        next
      }
      fh <- if (tf %in% files) heads[[tf]] else headings_of(readLines(tf, warn = FALSE))
      if (grepl("^\\s*[0-9]", frag)) {
        num <- norm(sub("^\\s*([0-9]+(\\.[0-9]+)*).*$", "\\1", frag))
        ok <- any(startsWith(norm(fh), paste0(num, " ")) | norm(fh) == num)
        if (!ok) add(f, i, "WARN", sprintf("section not found in %s: §%s", rel(tf), sub(" .*$", "", frag)))
      } else if (!matches_heading(frag, fh)) {
        lvl <- if (quoted && tf != f && !grepl("(^|/)openspec/changes/", f)) "ERROR" else "WARN"
        add(f, i, lvl, sprintf("section heading not found in %s: %s", rel(tf), substr(frag, 1L, 60L)))
      }
    }

    # Status header lines (top of file only; deeper ones are examples/templates)
    if (i <= 10L && grepl(status_rx, line)) {
      rest <- sub("^\\s*\\*{0,2}Status:\\*{0,2}\\s*", "", line)
      if (!grepl(version_rx, rest)) {
        add(f, i, "ERROR", sprintf("Status line missing `vX.Y (YYYY-MM-DD)`: %.60s", rest))
      }
    }
  }
}

if (length(problems)) cat(paste0(problems, collapse = "\n"), "\n\n", sep = "")
n_err <- sum(grepl(": ERROR: ", problems, fixed = TRUE))
cat(sprintf("check-docs: %d files, %d errors, %d warnings\n",
            length(files), n_err, sum(grepl(": WARN: ", problems, fixed = TRUE))))
quit(status = if (n_err > 0L) 1L else 0L)
