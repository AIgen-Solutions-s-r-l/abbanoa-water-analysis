#!/bin/bash
cd /home/alessio/Customers/Abbanoa
export PYTHONPATH=/home/alessio/Customers/Abbanoa:$PYTHONPATH
~/.local/bin/streamlit run src/presentation/web/dashboard.py --server.port 8502 --server.address 0.0.0.0