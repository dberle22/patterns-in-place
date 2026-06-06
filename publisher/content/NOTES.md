# Notes & Ideas
This file contains my general notes and thoughts on the analysis process.

## Topics vs Specific Questions
Thinking in topics to explore before picking a specific visual or question makes more sense. It's easier to pick a very specific question and visual like the national vacany rate and a line chart to show it, but it removes any kind of EDA and analysis. The more interesting approach is to select a topic, think of a few questions, perform an initial EDA, then see how the analysis comes together. We can create some rich charts, and build out a stronger narrative that can be turned into a longer form article. (2026-05-14)

## EDA

## Benchmarks
We still seem to struggle with Benchmarks. For example, getting all-CBSA was a bit more trouble then I wanted. We should think clearly about the benchmarks we want, possibly creating a dim_benchmark table to store the relationships between a geography and its' benchmarks. (2026-05-14)

## Outliers
How do we handle Outliers?

## CBSA Size
Should we filter to CBSAs larger than 250k or just use all CBSAs? CBSA already encodes a minimum size. But it could be interesting to set size buckets here: Small (250k-500k), Medium (500k-1M), Large (1M+), for example. (2026-05-14).

## Puerto Rico
We should remove Puerto Rico by default from our analysis. (2026-05-14)