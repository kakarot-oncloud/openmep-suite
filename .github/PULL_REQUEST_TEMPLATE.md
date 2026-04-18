## Summary

<!-- What does this PR do? One paragraph is enough. -->

## Type of Change

- [ ] Bug fix (calculation error, crash, wrong result)
- [ ] New calculation module
- [ ] New region / sub-authority support
- [ ] Standards data update (new table, corrected values)
- [ ] UI / Streamlit improvement
- [ ] API change (new endpoint, modified response schema)
- [ ] Documentation update
- [ ] Refactor / code quality
- [ ] CI / tooling

## Standards Reference

<!-- If this touches a calculation or data table, list the standard(s) and clause(s). -->
<!-- Example: BS 7671:2018 Table 4D5A, Reg 523 — cable current rating -->

| Standard | Clause / Table | Region |
|----------|----------------|--------|
|          |                |        |

## Testing Done

- [ ] Manual test in Streamlit UI with real inputs
- [ ] `curl` test against API endpoint
- [ ] All existing tests pass (`pytest backend/`)
- [ ] Verified result against hand calculation or published example

## Checklist

- [ ] Code follows the project's adapter pattern (`BaseElectricalAdapter`)
- [ ] New data tables include the source standard and edition in a comment
- [ ] No hardcoded credentials or secrets
- [ ] Docstrings updated if public interface changed
- [ ] `CHANGELOG.md` entry added

## Related Issues

Closes #
