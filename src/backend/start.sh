#!/bin/bash

WORK_DIR=$(dirname $0)
cd ${WORK_DIR}
uvicorn fd_backend:app --reload

