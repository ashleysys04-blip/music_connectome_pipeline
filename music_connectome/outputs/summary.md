# Analysis Summary

## Sample
- N after QC: 473
- N trained: 201

## Brain -> PSM  (glm_brain_behavior.csv)
```
          feature   n      beta       se         t        p       r2    q_fdr  sig_fdr
  small_worldness 306  0.129518 0.055058  2.352371 0.019298 0.129755 0.212277    False
       modularity 306  0.065266 0.058221  1.121000 0.263181 0.117440 0.967407    False
       FPN_within 306 -0.042979 0.055002 -0.781406 0.435178 0.115550 0.967407    False
       DMN_within 306  0.030418 0.056782  0.535702 0.592560 0.114600 0.967407    False
 char_path_length 306 -0.028407 0.055185 -0.514756 0.607101 0.114535 0.967407    False
global_efficiency 306  0.027215 0.055183  0.493185 0.622242 0.114471 0.967407    False
  mean_clustering 306  0.007761 0.054456  0.142519 0.886766 0.113816 0.967407    False
  FPN_MTL_between 306 -0.007323 0.056851 -0.128805 0.897598 0.113805 0.967407    False
  DMN_FPN_between 306  0.005132 0.055570  0.092344 0.926486 0.113781 0.967407    False
  DMN_MTL_between 306 -0.003506 0.053929 -0.065015 0.948205 0.113768 0.967407    False
       MTL_within 306 -0.002255 0.055150 -0.040894 0.967407 0.113761 0.967407    False
```

## Music -> PSM (primary)  (glm_music_behavior.csv)
```
         model   outcome            predictor      beta       se         t        p   n       r2    q_fdr sig_fdr
 M1_onset_only psm_score      music_onset_age -0.091900 0.088490 -1.038537 0.300421 184 0.130142      NaN     NaN
 M2_hours_only psm_score log_cumulative_hours -0.038824 0.080124 -0.484542 0.628597 183 0.127092      NaN     NaN
M4_interaction psm_score      music_onset_age -0.215214 0.117924 -1.825019 0.069693 183 0.143322      NaN     NaN
M4_interaction psm_score log_cumulative_hours -0.159579 0.103909 -1.535765 0.126392 183 0.143322      NaN     NaN
M4_interaction psm_score        onset_x_hours  0.030073 0.091329  0.329281 0.742335 183 0.143322      NaN     NaN
       M3_both psm_score      music_onset_age -0.206933 0.114921 -1.800656 0.073460 183 0.142795 0.128818   False
       M3_both psm_score log_cumulative_hours -0.157983 0.103534 -1.525907 0.128818 183 0.142795 0.128818   False
```

## Music -> Brain  (glm_music_brain.csv)
```
    brain_feature            predictor   n      beta       se         t        p       r2    q_fdr  sig_fdr
  DMN_FPN_between log_cumulative_hours 175  0.125209 0.107944  1.159943 0.247708 0.082665 0.710554    False
       MTL_within log_cumulative_hours 175  0.121686 0.111996  1.086522 0.278796 0.032731 0.710554    False
  small_worldness log_cumulative_hours 175 -0.106101 0.108953 -0.973832 0.331532 0.063234 0.710554    False
  mean_clustering log_cumulative_hours 175  0.085600 0.110611  0.773887 0.440079 0.075580 0.710554    False
       DMN_within log_cumulative_hours 175  0.075728 0.107135  0.706847 0.480635 0.059344 0.710554    False
 char_path_length log_cumulative_hours 175 -0.073333 0.108291 -0.677190 0.499211 0.118203 0.710554    False
       modularity log_cumulative_hours 175  0.070073 0.106274  0.659358 0.510564 0.094419 0.710554    False
       FPN_within log_cumulative_hours 175  0.061874 0.105875  0.584403 0.559728 0.044879 0.710554    False
global_efficiency log_cumulative_hours 175  0.060177 0.108925  0.552462 0.581362 0.093699 0.710554    False
  FPN_MTL_between log_cumulative_hours 175  0.039606 0.112464  0.352164 0.725154 0.012919 0.797669    False
  DMN_MTL_between log_cumulative_hours 175 -0.001897 0.111794 -0.016965 0.986484 0.017231 0.986484    False
  small_worldness      music_onset_age 175 -0.129500 0.120290 -1.076561 0.283211 0.063234 0.946628    False
  DMN_FPN_between      music_onset_age 175 -0.079177 0.119176 -0.664372 0.507358 0.082665 0.946628    False
       FPN_within      music_onset_age 175 -0.068923 0.116892 -0.589631 0.556225 0.044879 0.946628    False
global_efficiency      music_onset_age 175 -0.055213 0.120259 -0.459119 0.646739 0.093699 0.946628    False
       DMN_within      music_onset_age 175 -0.052606 0.118283 -0.444745 0.657073 0.059344 0.946628    False
 char_path_length      music_onset_age 175  0.049516 0.119559  0.414153 0.679287 0.118203 0.946628    False
  mean_clustering      music_onset_age 175 -0.032811 0.122121 -0.268680 0.788504 0.075580 0.946628    False
  DMN_MTL_between      music_onset_age 175 -0.032428 0.123427 -0.262730 0.793079 0.017231 0.946628    False
       MTL_within      music_onset_age 175  0.030948 0.123650  0.250286 0.802671 0.032731 0.946628    False
  FPN_MTL_between      music_onset_age 175 -0.014327 0.124167 -0.115386 0.908276 0.012919 0.946628    False
       modularity      music_onset_age 175  0.007866 0.117333  0.067041 0.946628 0.094419 0.946628    False
```

## Mediation  (mediation_results.csv)
```
         mediator         a         b         c   c_prime        ab    ci_low  ci_high  p_boot   n  ci_excludes_zero
  small_worldness -0.129500  0.124747 -0.236001 -0.219846 -0.016155 -0.062604 0.019927  0.4024 175             False
       DMN_within -0.052606  0.093948 -0.236001 -0.231059 -0.004942 -0.041335 0.023834  0.7196 175             False
 char_path_length  0.049516 -0.079857 -0.236001 -0.232047 -0.003954 -0.027600 0.018419  0.7532 175             False
  DMN_FPN_between -0.079177  0.071095 -0.236001 -0.230372 -0.005629 -0.037168 0.023966  0.7860 175             False
global_efficiency -0.055213  0.059741 -0.236001 -0.232702 -0.003298 -0.029731 0.020682  0.8168 175             False
       FPN_within -0.068923  0.059444 -0.236001 -0.231904 -0.004097 -0.030355 0.023688  0.8380 175             False
  DMN_MTL_between -0.032428  0.064201 -0.236001 -0.233919 -0.002082 -0.033725 0.024141  0.8628 175             False
  FPN_MTL_between -0.014327  0.076036 -0.236001 -0.234911 -0.001089 -0.031051 0.022334  0.8664 175             False
       MTL_within  0.030948  0.042111 -0.236001 -0.237304  0.001303 -0.019213 0.029274  0.8676 175             False
  mean_clustering -0.032811  0.056132 -0.236001 -0.234159 -0.001842 -0.026716 0.021369  0.9120 175             False
       modularity  0.007866  0.060184 -0.236001 -0.236474  0.000473 -0.024647 0.023130  0.9936 175             False
```
