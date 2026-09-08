# POI Taxonomy Workflow

This directory will hold approved, versioned mappings and durable overrides
when Epic 4 begins. It is intentionally empty of production mappings today.

Profile raw source categories first. Promote only reviewed decisions into a
mapping rule with a stable rule ID, mapping version, rationale, evidence, and
review state. Keep consumer baskets such as `daily_needs` in their analyses,
not in this taxonomy.

Start with the plain-language [Taxonomy Guide](TAXONOMY_GUIDE.md). The first
approved Overture rules are in [q4_overture_v1.yml](q4_overture_v1.yml).

Use [the taxonomy exploration notebook](TAXONOMY_EXPLORATION_NOTEBOOK.py) to
profile unmapped source values and inspect examples before proposing a new rule.
