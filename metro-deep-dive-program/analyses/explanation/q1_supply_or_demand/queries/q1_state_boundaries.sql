-- Lower-48 state outlines give the national CBSA-centroid map readable context.
select state_abbr, state_name, geom_wkb
from geo.states
where state_abbr not in ('AK', 'HI', 'PR', 'AS', 'GU', 'MP', 'VI');
