# Crop rotation engine

Knowledge templates cover cotton, wheat, rice, mung bean, chickpea, millet, sorghum, sunflower, mustard, maize, sesame, and berseem. CSVs contain headers only: do not populate agronomic values until sources and local expert review are documented. Each fact stores evidence source, region/context, units, effective version, and expert verification status.

Decision flow: model crop probabilities → generate candidate sequences → apply hard agronomic constraints → apply soft penalties → include farmer priorities → rank rotations → return existing plus alternatives → explain evidence, benefits, risks and limitations → flag local review requirements.

Hard constraints must be evidence-backed and conservative; unknown inputs cannot silently pass as safe. Soft scores expose their criteria/weights and uncertainty. Farmer priorities affect ranking only within feasible candidates. Preserve the baseline rotation, compare alternatives, and record model/knowledge versions and the reason each candidate was excluded or ranked. An expert review gate is required before operational recommendation.
