pip install autoflake black isort -q
isort .
black .
autoflake --in-place  --remove-all-unused-imports --recursive .