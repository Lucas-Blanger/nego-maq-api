#!/bin/sh
# entrypoint.sh

echo "Aguardando o banco de dados subir..."
sleep 10  # dá um tempo para o MySQL iniciar

echo "Rodando seed..."
python -m seeders.seed

echo "Iniciando Gunicorn..."
exec gunicorn -b 0.0.0.0:5000 app:app
