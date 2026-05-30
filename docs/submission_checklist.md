# SilicaFold V0 - Submission Checklist

## Final Status: ✅ READY FOR SUBMISSION

**Verified**: 2026-05-30  
**Commit**: `1cb13539da636b466314b0a9656875c877b38b6f`  
**Evidence**: See [current_submission_status.md](current_submission_status.md) and [submission_review.md](submission_review.md)

---

## Pre-Submission Checklist

Use this checklist before submitting to Tiny Tapeout. All items should be verified with actual generated artifacts, not conceptual estimates.

### 1. Design Verification

- [ ] All cocotb tests pass locally
  ```bash
  cd test && make
  ```
- [ ] No Verilog syntax errors
  ```bash
  cd src && iverilog -g2005 -Wall -t null *.v
  ```
- [ ] Reset behavior verified (all outputs clear on rst_n)
- [ ] uio_oe is correctly set to `8'b1111_0000`
- [ ] No inferred latches in synthesis

### 2. GitHub Actions

- [ ] Test workflow passes (green checkmark)
- [ ] GDS workflow completes successfully
- [ ] All artifacts uploaded correctly

### 3. Synthesis Results

From GDS workflow artifacts, verify:

- [ ] Synthesis completes without errors
- [ ] No critical warnings in synthesis log
- [ ] Cell count is reasonable for tile allocation
- [ ] No black boxes or missing modules

### 4. Timing Closure

- [ ] Setup time met (positive slack or zero)
- [ ] Hold time met
- [ ] Clock frequency achievable (25 MHz target)
- [ ] No timing violations in critical paths

Location in artifacts:
- `reports/synthesis/*/timing.rpt`
- `reports/routing/*/timing.rpt`
- `reports/signoff/*/timing.rpt`

### 5. Area Utilization

- [ ] Design fits within allocated tiles (4x2)
- [ ] Utilization is reasonable (typically 30-70%)
- [ ] No placement failures
- [ ] Routing completed successfully

Location in artifacts:
- `reports/*/utilization.rpt`
- `reports/*/area.rpt`

### 6. Physical Verification

- [ ] DRC clean (zero violations)
- [ ] LVS clean (netlist matches layout)
- [ ] Antenna rule violations addressed
- [ ] Metal density within limits

Location in artifacts:
- `reports/signoff/*drc*.rpt`
- `reports/signoff/*lvs*.rpt`

### 7. GDS Generation

- [ ] Final GDS file generated
- [ ] GDS file size is reasonable
- [ ] GDS can be opened in viewer (KLayout)

Location in artifacts:
- `results/final/gds/*.gds` or `*.gds.gz`

### 8. Documentation

- [ ] info.yaml is complete and valid
- [ ] README is accurate and current
- [ ] Pin descriptions match implementation
- [ ] All source files listed in info.yaml

### 9. Final Review

- [ ] Download all artifacts from GitHub Actions
- [ ] Run `scripts/check_gds_artifacts.sh`
- [ ] Run `scripts/summarize_openlane_reports.py`
- [ ] Update README with actual PPA numbers (not estimates)
- [ ] Remove or update any placeholder values

## Post-Build Verification

After GDS generation succeeds:

### Update README.md

Replace conceptual statements with actual values:

```markdown
## Actual PPA (from OpenLane)

| Metric | Value |
|--------|-------|
| Cell Count | [from synthesis report] |
| Utilization | [from utilization report]% |
| Worst Slack | [from timing report] ns |
| Total Area | [from area report] um² |
```

### Archive Reports

Copy key reports to `reports/` directory:
- Timing summary
- Utilization summary
- DRC summary
- LVS summary

### Visual Verification

If PNG/SVG renders are generated:
- [ ] Layout looks reasonable
- [ ] No obvious routing issues
- [ ] Power/ground rails visible
- [ ] Standard cell rows organized

## Common Issues

### Timing Failure
- Reduce clock frequency in info.yaml
- Simplify critical paths
- Add pipeline stages if needed

### Area Overflow
- Increase tile count
- Optimize RTL (reduce register count)
- Check for unnecessary logic

### DRC Violations
- Usually fixed by re-running with different settings
- Check OpenLane logs for specific violations
- May indicate routing congestion

### LVS Mismatch
- Verify all ports are connected
- Check for floating nodes
- Review synthesis warnings

## Submission

Once all checks pass:

1. Go to [tinytapeout.com](https://tinytapeout.com)
2. Create or log into your account
3. Start new submission
4. Link your GitHub repository
5. Select tile count
6. Complete payment
7. Wait for confirmation

## Support

- [Tiny Tapeout Discord](https://discord.gg/tinytapeout)
- [GitHub Issues](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/issues)
- [Tiny Tapeout FAQ](https://tinytapeout.com/faq)
