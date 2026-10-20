#!/bin/sh
set -eu

python -m app.init_db
exec "$@"
