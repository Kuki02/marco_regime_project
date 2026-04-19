# Macro Regime Project

## Overview
This project builds a macroeconomic regime framework by collecting, processing, and analyzing financial and economic data.

It currently focuses on:
- US yield curve
- Corporate bond spreads
- Data automation and weekly updates

The goal is to create a structured system for macro analysis and trade idea generation.

---

## Project Structure

- `scripts/` → data collection and update scripts  
- `config/` → configuration files and data mappings  
- `data/` → raw and processed datasets (not tracked in Git)  
- `outputs/` → generated results and exports (not tracked)  
- `notebooks/` → analysis and research  
- `docs/` → documentation  

---

## How to Run

### 1. Activate environment
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt