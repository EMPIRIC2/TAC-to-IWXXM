#!/bin/bash
set -e

echo "=== Reorganizing IWXXM Schemas ==="

# Backup current structure
echo "Step 1: Creating backups..."
cp -r iwxxm iwxxm-backup
cp -r iwxxm-modelling iwxxm-modelling-backup

# Setup IWXXM 2023-1
echo "Step 2: Setting up IWXXM 2023-1..."
cd iwxxm
git fetch --all
mkdir -p ../iwxxm-temp/2023-1
git archive e84bf544702e6a3c638e7ab5f02a9c930dda57f7 | tar -x -C ../iwxxm-temp/2023-1
cd ..

# Setup IWXXM 2025-2 (current master/v2025-2 tag)
echo "Step 3: Setting up IWXXM 2025-2..."
cd iwxxm
mkdir -p ../iwxxm-temp/2025-2
git archive HEAD | tar -x -C ../iwxxm-temp/2025-2
cd ..

# Setup IWXXM-Modelling 2023-1 
echo "Step 4: Setting up IWXXM-Modelling 2023-1..."
cd iwxxm-modelling
git fetch --all  
mkdir -p ../iwxxm-modelling-temp/2023-1
git archive 2c1edcdabf26792263ab214df9531665e3b5a867 | tar -x -C ../iwxxm-modelling-temp/2023-1
cd ..

# Setup IWXXM-Modelling 2025-2
echo "Step 5: Setting up IWXXM-Modelling 2025-2..."
cd iwxxm-modelling
mkdir -p ../iwxxm-modelling-temp/2025-2
git archive HEAD | tar -x -C ../iwxxm-modelling-temp/2025-2
cd ..

# Replace old structure with new versioned structure
echo "Step 6: Replacing directory structure..."
rm -rf iwxxm iwxxm-modelling
mv iwxxm-temp iwxxm
mv iwxxm-modelling-temp iwxxm-modelling

echo "✓ Schema reorganization complete!"
echo "Structure:"
ls -la iwxxm/
ls -la iwxxm-modelling/
