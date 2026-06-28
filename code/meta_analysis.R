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

# ---- summary forest plot ----------------------------------------------------
dir.create("output/figures", recursive = TRUE, showWarnings = FALSE)
ord <- res %>% arrange(pool_family, estimate_r)
pd  <- ord %>% mutate(pool_name = factor(pool_name, levels = pool_name))
p <- ggplot(pd, aes(estimate_r, pool_name)) +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey60") +
  geom_segment(aes(x = pi_low_r, xend = pi_high_r, y = pool_name, yend = pool_name),
               linewidth = 0.4, colour = "grey70") +
  geom_segment(aes(x = ci_low_r, xend = ci_high_r, y = pool_name, yend = pool_name),
               linewidth = 0.9) +
  geom_point(aes(size = k), shape = 18) +
  geom_text(aes(label = sprintf("%.2f [%.2f, %.2f]", estimate_r, ci_low_r, ci_high_r)),
            hjust = 0, nudge_y = 0.30, size = 2.6) +
  scale_size_continuous(range = c(2.5, 4.5), guide = "none") +
  scale_x_continuous(limits = c(-1.05, 1.25), breaks = seq(-1, 1, 0.5)) +
  labs(x = "Pooled correlation r (thick line 95% CI, thin line 95% prediction interval)",
       y = NULL) +
  theme_classic(base_size = 10)
ggsave("output/figures/forest.png", p, width = 7.4, height = 3.0, dpi = 600)

cat("\nWrote intermediate/pooled_estimates.csv and output/figures/forest.png\n")
