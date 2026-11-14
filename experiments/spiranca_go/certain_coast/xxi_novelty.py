"""The innovation paragraphs of reviews X and XI of the author's series (State of the art X: placing sensors that
interfere; State of the art XI: warnings for what happens between samples), as written in the reviews, with the
review-internal labels of the anchor articles (A1, A2, Table 1) replaced by their names."""

X = ('**INTERVENTION-GO** turns sensor interference from a nuisance into a design variable. (1) Reference channels that '
     'see only the error — a barometer, a sealed channel on each logger hub — enter the search beside the piezometers, '
     'valued by the exact criterion that alone can see them (Proposition N1). (2) The correction is exact '
     'marginalisation, and the corrected data reproduce the interference-free estimate (Proposition N2(i)). (3) A '
     'ceiling bounds what any correction can achieve (Proposition N2(ii)). (4) The worst case is found exactly in the '
     'amplitudes and by an adversary with exact data-space gradients in the shapes (Proposition N3), which replaces '
     'the eigenvalue sensitivities of the robust design of Chowdhary, Attia and Alexanderian. (5) Every robust '
     'network carries a certified gap, which that design lacks, built from a relaxation that is tightened by the '
     'ceiling and by enumerating the reference channels (Proposition N4). To our knowledge, neither that article nor '
     'the Certified OED framework, nor the other sources of review X, places reference channels by optimal design or '
     'certifies a robust network.')

XI = ('**PATH-GO** turns the robust bounds of mathematical finance and the online forecasts of neural jump ODEs into '
      'certified warnings for an event the samples rarely see: the crossing of a limit between two samples. (1) It '
      'shows that sparse sampling, which fixes only the marginal law, cannot bound this crossing from above '
      '(Proposition S1, through Slepian\'s inequality). (2) It gives the information a pair of samples carries on the '
      'time scale in closed form, so the monitoring design can buy exactly the observation that closes the band '
      '(Proposition S2). (3) It computes the band over all models consistent with the records, as robust pricing with '
      'neural SDEs (Gierjatowicz et al., 2020) does for an exotic option, and certifies it for a single site with a '
      'conformal margin (Proposition S3), which that work lacks. (4) It issues the warning online as the conditional '
      'probability that the path-dependent neural jump ODE (Krach, Nübel and Teichmann) learns, with the observed path '
      'and a head logger as inputs (Proposition S4). To our knowledge, neither of the two works nor the other sources '
      'of review XI bounds or certifies crossings between samples of an environmental record.')
