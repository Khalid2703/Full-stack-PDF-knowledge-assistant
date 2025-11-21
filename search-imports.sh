#!/bin/bash

# Search for any remaining sentence_transformers imports

echo "🔍 Searching for sentence_transformers imports..."
echo ""

# Search in Python files
grep -r "sentence_transformers" C:/Users/hp/Regnova/backend --include="*.py" 2>/dev/null || echo "✅ No imports found in .py files"

# Search in requirements
grep -r "sentence-transformers" C:/Users/hp/Regnova/backend --include="requirements*.txt" 2>/dev/null || echo "✅ No entries in requirements.txt"

echo ""
echo "Done!"
