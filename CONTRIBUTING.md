# Contributing

1. Read the root README, coding standards, and applicable ADRs before changing architecture.
2. Work on a focused branch. Do not rewrite user data or raw datasets.
3. Keep raw/interim/processed data, secrets, local volumes, and model artifacts out of Git.
4. Update schemas and documentation when changing data contracts.
5. Validate CSV headers, JSON/YAML syntax, Markdown links, and ignore rules relevant to a change. Add focused automated tests as implementation begins.
6. Do not use fabricated environmental measurements, crop parameters, farmer records, or model outputs in examples. Label synthetic software fixtures explicitly if later required.
7. Record material architecture changes as ADRs.
8. Never deploy, publish data, or transmit farmer information without the project owner's explicit authorization.
