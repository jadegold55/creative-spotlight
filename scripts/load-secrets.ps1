Write-Host "Pulling secrets from AWS Parameter Store..."

$parameters = aws ssm get-parameters-by-path `
  --path "/creativespotlight/" `
  --with-decryption `
  --query "Parameters[*].[Name,Value]" `
  --output text

$parameters -split "`n" | ForEach-Object {
    if ($_.Trim() -ne "") {
        $parts = $_ -split "`t"
        $key = Split-Path $parts[0] -Leaf
        $value = $parts[1]
        "$key=$value"
    }
} | Set-Content .env

Write-Host "Done. .env file created."