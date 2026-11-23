#!/usr/bin/env Rscript
# =============================================================================
# meta_analysis.R -- reproduce the six random-effects pooled correlations
# (manuscript Table 3 / forest figure) from the deposited per-study pooling
# inputs. The pool_inputs sheet carries yi (Fisher-z transformed correlation)
# and vi (its sampling variance), one row per independent study per pool, so the
# pooling re-runs without the copyright-restricted source text.
#
#   input : intermediate/pool_inputs.csv
#   output: intermediate/pooled_estimates.csv   (feeds build_tables.py, Table 3)
#           output/figures/forest.png           (summary forest plot)
# =============================================================================
suppressPackageStartupMessages({
  library(metafor); library(dplyr); library(readr); library(ggplot2)
})

PRIMARY_MIN_K <- 5                       # a family is pooled only with >= 5 independent studies
z2r <- function(z) (exp(2 * z) - 1) / (exp(2 * z) + 1)   # inverse Fisher-z

ap <- read_csv("intermediate/pool_inputs.csv", show_col_types = FALSE) %>%
  mutate(yi = as.numeric(yi), vi = as.numeric(vi))

pools <- ap %>%
  group_by(pool_family, pool_label, pool_name) %>%
  summarise(k = n_distinct(study_id), .groups = "drop") %>%
  filter(k >= PRIMARY_MIN_K) %>%
  arrange(desc(k))

fit_one <- function(pl) {
  d  <- filter(ap, pool_label == pl)
  m  <- rma(yi = yi, vi = vi, data = d, method = "REML")
  pr <- predict(m)                       # prediction interval on the z scale
  inf <- if (z2r(m$ci.lb) > 0) "supported_positive"
         else if (z2r(m$ci.ub) < 0) "supported_negative"
         else "not_supported"
  tibble(
    pool_label = pl,
    pool_name  = pools$pool_name[match(pl, pools$pool_label)],
    pool_family = pools$pool_family[match(pl, pools$pool_label)],
    k = m$k, k_studies = m$k,
    estimate_z = as.numeric(m$b), se_z = m$se,
    estimate_r = z2r(as.numeric(m$b)),
    ci_low_r = z2r(m$ci.lb), ci_high_r = z2r(m$ci.ub),
    pi_low_r = z2r(pr$pi.lb), pi_high_r = z2r(pr$pi.ub),
    p_value = m$pval, tau2 = m$tau2, I2 = m$I2, inference = inf)
}

res <- bind_rows(lapply(pools$pool_label, fit_one))

dir.create("intermediate", showWarnings = FALSE)
write_csv(res, "intermediate/pooled_estimates.csv")

cat("\n== Pooled random-effects correlations (REML, Fisher-z) ==\n")
res %>%
  transmute(pool_name, k,
            r = round(estimate_r, 3),
            CI = sprintf("[%.3f, %.3f]", ci_low_r, ci_high_r),
            PI = sprintf("[%.3f, %.3f]", pi_low_r, pi_high_r),
            I2 = round(I2, 1), inference) %>%
  as.data.frame() %>% print(row.names = FALSE)

# Figure 2 shows pooled estimates and 95% confidence intervals.
dir.create("output/figures", recursive = TRUE, showWarnings = FALSE)
theme_pub <- function(base_size = 8, axis_title_size = 9) {
  theme_classic(base_size = base_size, base_family = "Helvetica") %+replace%
    theme(
      axis.line = element_line(colour = "black", linewidth = 0.45),
      axis.ticks = element_line(colour = "black", linewidth = 0.35),
      axis.ticks.length = unit(-0.10, "cm"),
      axis.title = element_text(size = axis_title_size, colour = "black"),
      axis.text = element_text(size = base_size, colour = "black"),
      panel.grid = element_blank(),
      plot.title = element_blank(),
      plot.background = element_rect(fill = "white", colour = NA),
      panel.background = element_rect(fill = "white", colour = NA),
      legend.position = "none"
    )
}
okabe <- c(
  "H1_source_to_SA" = "#0072B2",
  "H2_SA_pleasantness" = "#E69F00",
  "SA_comfort_quality" = "#009E73",
  "index_to_SA" = "#D55E00"
)
name_order <- c(
  "SA and comfort or quality",
  "SA and pleasantness",
  "Sound level to SA",
  "Loudness to SA",
  "Human or social sounds to SA",
  "Natural sounds to SA"
)
fig <- res %>%
  mutate(
    pool_name = factor(paste0(pool_name, " (k = ", k, ")"),
                       levels = paste0(name_order, " (k = ", res$k[match(name_order, res$pool_name)], ")"))
  ) %>%
  ggplot(aes(x = estimate_r, y = pool_name, colour = pool_family)) +
  geom_vline(xintercept = 0, linewidth = 0.35, linetype = "dashed", colour = "grey45") +
  geom_errorbar(aes(xmin = ci_low_r, xmax = ci_high_r), orientation = "y", width = 0.18, linewidth = 0.45) +
  geom_point(size = 1.8) +
  scale_colour_manual(values = okabe) +
  scale_x_continuous(limits = c(-1, 1), breaks = seq(-1, 1, 0.5)) +
  labs(x = "Pooled correlation (r)", y = NULL) +
  theme_pub()
ggsave("output/figures/forest.png", fig, width = 178 / 25.4, height = 120 / 25.4, dpi = 600, bg = "white")

cat("\nWrote intermediate/pooled_estimates.csv and output/figures/forest.png\n")
