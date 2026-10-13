---
name: masalahealth-setup
description: Check the MasalaHealth plugin's Open Masala connection after installation and explain the supported workflows and data scope.
---

# Set up MasalaHealth

Explain that this version uses Open Masala's cited South Asian references with measurements the user supplies. It does not connect to the user's Masala app records or retrieve recovery history.

Discover Open Masala tools and call `list_measures` without personal inputs to verify the connection and describe its actual coverage. If unavailable, report that setup is incomplete and direct the user to the plugin's connection settings. Do not solicit secrets in chat or claim installation/authentication succeeded merely because instructions were loaded.

Offer a lab comparison, an evidence lookup, or appointment preparation. For the chosen workflow, use the bundled masalahealth-review skill. Ask only for facts needed by that workflow. Do not request an entire medical record as a setup requirement.
