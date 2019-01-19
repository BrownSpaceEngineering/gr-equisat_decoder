#!/usr/bin/env bash
echo "Generating key..."
key=$(curl -s -X POST http://api.brownspace.org/equisat/generate-key)
echo "Your API key is: $key"
echo "Pass this as an argument to equisat.py using --api_key='$key'"