#!/bin/bash
echo "Pulling secrets from AWS Parameter Store..."

aws ssm get-parameters-by-path \
  --path "/creativespotlight/" \
  --with-decryption \
  --region us-east-2 \
  --query "Parameters[*].[Name,Value]" \
  --output text | while IFS=$'\t' read -r name value; do
    key=$(basename "$name")
    echo "$key=$value"
done > .env

echo "Done. .env file created."