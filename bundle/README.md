# SML-RECALL BUNDLE TIER

Welcome to the Bundle Tier. This directory contains enterprise-grade integrations and advanced workflows designed for power users who want to integrate SML-RECALL into their automated systems and CI/CD pipelines.

## Contents

1. `ci-integration.py` - A script designed to run in your GitHub Actions or GitLab CI pipeline. It analyzes pull requests against your `decision-log.md` and `MASTER.md` to ensure architectural consistency before code is merged.
2. `webhook-listener.py` - A lightweight server that listens for webhooks from external services (like Jira, Trello, or GitHub) and automatically updates your `thread-tracker.md` to keep your external brain synced with your issue trackers.
3. `team-sync.py` - A utility to merge multiple `MASTER.md` files from a team into a single synchronized project state document.

*More scripts will be added to this tier as the product evolves.*
