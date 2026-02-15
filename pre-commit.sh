# /bin/bash

# Re-format staged files only

INCLUDE_EXTENSIONS="py"

git diff --name-only --cached | while read -r file; do
  if [ -f "$file" ]; then
    # Get file extension
    extension="${file##*.}"
    
    # Check if extension exactly matches one in INCLUDE_EXTENSIONS
    if echo "$INCLUDE_EXTENSIONS" | tr ',' '\n' | grep -Fx "$extension" > /dev/null; then
      echo "Formatting $file"
      uvx autoflake --in-place --remove-all-unused-imports "$file"
      uvx black "$file"
      uvx isort "$file"
    fi
  fi
done

# update staged files
git update-index --again

# Run build
uv build