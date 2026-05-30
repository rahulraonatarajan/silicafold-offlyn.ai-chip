# Local Hardening Guide

## Overview

This guide explains how to run the Tiny Tapeout/OpenLane hardening flow locally. **GitHub Actions is the primary and recommended path for beginners.** Local hardening is optional and intended for advanced users who want faster iteration or offline development.

## Prerequisites

### Option 1: Docker (Recommended for Local)

Docker provides a consistent environment matching the GitHub Actions runner.

```bash
# Install Docker
# macOS: brew install --cask docker
# Linux: Follow docker.com instructions
# Windows: Docker Desktop

# Verify Docker is running
docker --version
docker run hello-world
```

### Option 2: Native Installation

For native installation, you need:
- Python 3.8+
- Yosys (synthesis)
- OpenROAD (place and route)
- Magic (DRC)
- Netgen (LVS)
- KLayout (viewing)
- SKY130 PDK

This is complex and not recommended unless you're experienced.

## Using Tiny Tapeout's Local Flow

Tiny Tapeout provides a local hardening option. Check the official documentation:
- [Tiny Tapeout Documentation](https://tinytapeout.com/docs/)
- [TT GitHub Template](https://github.com/TinyTapeout/tt-verilog-demo)

### Quick Start (Docker)

```bash
# Clone the Tiny Tapeout tools (check for current version)
git clone https://github.com/TinyTapeout/tt-support-tools.git
cd tt-support-tools

# Or use the official action locally via act
# (requires act: https://github.com/nektos/act)
```

## Manual OpenLane Flow

For direct OpenLane usage (advanced):

### 1. Install OpenLane

```bash
# Clone OpenLane
git clone https://github.com/The-OpenROAD-Project/OpenLane.git
cd OpenLane

# Run installation
make

# Verify
make test
```

### 2. Set Up Design

```bash
# Create design directory
mkdir -p designs/silicafold_v0

# Copy source files
cp /path/to/silicafold/src/*.v designs/silicafold_v0/src/

# Create config.json
cat > designs/silicafold_v0/config.json << 'EOF'
{
    "DESIGN_NAME": "tt_um_rahulraonatarajan_silicafold_v0",
    "VERILOG_FILES": "dir::src/*.v",
    "CLOCK_PORT": "clk",
    "CLOCK_PERIOD": 40.0,
    "FP_SIZING": "absolute",
    "DIE_AREA": "0 0 200 200",
    "FP_PDN_AUTO_ADJUST": true
}
EOF
```

### 3. Run Hardening

```bash
# Interactive mode
./flow.tcl -interactive

# Or batch mode
./flow.tcl -design silicafold_v0
```

### 4. Check Results

```bash
# Results location
ls designs/silicafold_v0/runs/*/results/final/gds/

# Reports location
ls designs/silicafold_v0/runs/*/reports/
```

## Troubleshooting

### Docker Issues

```bash
# Reset Docker
docker system prune -a

# Check resources (Docker Desktop)
# Ensure at least 8GB RAM allocated

# Permission issues (Linux)
sudo usermod -aG docker $USER
# Then log out and back in
```

### Synthesis Failures

- Check for syntax errors: `iverilog -t null src/*.v`
- Verify module names match
- Check for unsupported constructs

### Timing Violations

- Increase clock period
- Simplify critical paths
- Check for combinational loops

### DRC Violations

- Usually routing congestion
- Try increasing die area
- Adjust placement density

### LVS Mismatches

- Verify all ports connected
- Check for floating nodes
- Review power connections

## When to Use Local Hardening

**Use GitHub Actions when:**
- First-time users
- Quick verification
- Official submission preparation
- Reproducible results needed

**Use local hardening when:**
- Rapid iteration needed
- No internet access
- Debugging complex issues
- Experimenting with configurations
- Learning the flow internals

## Comparison

| Aspect | GitHub Actions | Local |
|--------|----------------|-------|
| Setup | None | Complex |
| Speed | Minutes wait | Immediate start |
| Consistency | High | Varies |
| Debugging | Limited | Full access |
| Cost | Free (public repos) | Your hardware |
| Recommended | Yes | Advanced users |

## Files Produced

Both flows produce similar artifacts:
- GDS file (final layout)
- DEF file (design exchange format)
- LEF file (abstract view)
- Verilog netlist (gate-level)
- SDF file (timing)
- Reports (timing, area, DRC, LVS)

## Best Practices

1. **Always verify with GitHub Actions** before submission
2. **Don't modify OpenLane config** unless necessary
3. **Keep track of which flow** produced which results
4. **Document any local modifications** for reproducibility
5. **Use version control** for configuration changes

## Resources

- [OpenLane Documentation](https://openlane.readthedocs.io/)
- [Tiny Tapeout FAQ](https://tinytapeout.com/faq/)
- [SKY130 PDK Docs](https://skywater-pdk.readthedocs.io/)
- [OpenROAD Documentation](https://openroad.readthedocs.io/)

## Disclaimer

Local hardening results should match GitHub Actions, but minor differences are possible due to:
- Tool versions
- Random seeds
- System resources
- PDK versions

Always use GitHub Actions as the authoritative source for submission.
