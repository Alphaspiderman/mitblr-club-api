# Disable Virtual ENV Creation
poetry config virtualenvs.create false
# Just install
poetry install --no-interaction --no-ansi
# Debugging messages
echo Done Installing
pip freeze
echo Starting Server
# Start the server
poetry run task server
