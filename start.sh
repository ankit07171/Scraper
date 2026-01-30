#!/usr/bin/env bash

streamlit run dashboard.py \
  --server.port=$1845 \
  --server.address=0.0.0.0
