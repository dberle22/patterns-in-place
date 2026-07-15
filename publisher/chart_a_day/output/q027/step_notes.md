# Step Notes for q027

- [2026-07-12 22:20:00] Built the q027 state-level bivariate map from `gold.housing_core_wide`, using rent-to-income ratio on the horizontal dimension and an inverted vacancy metric on the vertical dimension so higher values mean tighter vacancy pressure.
- [2026-07-12 22:20:00] Both the R and Python paths rendered successfully on the first attempt once the geometry extract was in place. This was a good sign that the shared bivariate map prep/render infrastructure is now stable enough for real content questions.
- [2026-07-12 22:20:00] The key interpretive choice here is the sign inversion on vacancy. That assumption is explicit in both the SQL note and the subtitle/caption so the audience is not asked to infer why the vertical legend reads "higher = worse."
- [2026-07-12 22:20:00] The Python map is analytically correct but still more compact and less polished than the R reference. R devotes more room to the bivariate key and the national map footprint, which makes the high-high and low-low quadrants easier to decode.
- [2026-07-12 22:20:00] Side-by-side verdict for q027: `match_with_minor_drift`. This closes the `bivariate_choropleth` proof point and confirms that the current gap is mostly design polish rather than shared logic breakage.
