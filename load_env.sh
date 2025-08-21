#!/bin/bash
# Load environment variables from .env file
export $(cat .env | xargs)
echo "✅ Environment variables loaded from .env file"
