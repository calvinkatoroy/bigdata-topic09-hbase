param([string]$Name,[string]$Bash,[int]$Cols=170,[int]$Lines=42,[int]$TimeoutSec=900)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;using System.Runtime.InteropServices;
public class W{[DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out RECT r);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("user32.dll")]public static extern bool SetWindowPos(IntPtr h,IntPtr a,int x,int y,int cx,int cy,uint f);
public struct RECT{public int L,T,R,B;}}
"@
$D='C:\Users\calvi\Documents\BIG_DATA\6\Topic09_HBase'
$done="$D\$Name.done"; Remove-Item $done -ErrorAction SilentlyContinue
$inner="$Bash; touch /mnt/c/Users/calvi/Documents/BIG_DATA/6/Topic09_HBase/$Name.done; sleep 600"
$p=Start-Process conhost.exe -ArgumentList "cmd /c mode con cols=$Cols lines=$Lines & title $Name & wsl -d Ubuntu-24.04 -u root -- bash -c `"$inner`"" -PassThru
$t=0; while(-not (Test-Path $done) -and $t -lt $TimeoutSec){Start-Sleep 2;$t+=2}
Start-Sleep 2
$h=[IntPtr]::Zero;for($i=0;$i -lt 10 -and $h -eq 0;$i++){$w=Get-Process | ?{$_.MainWindowTitle -like "*$Name*" -and $_.MainWindowHandle -ne 0}|select -First 1;if($w){$h=$w.MainWindowHandle}else{Start-Sleep 1}}
if($h -eq 0){throw "no window"}
[W]::SetWindowPos($h,[IntPtr](-1),20,20,0,0,0x1 -bor 0x40)|Out-Null
[W]::SetForegroundWindow($h)|Out-Null; Start-Sleep 1
$r=New-Object W+RECT; [W]::GetWindowRect($h,[ref]$r)|Out-Null
$bmp=New-Object Drawing.Bitmap ($r.R-$r.L),($r.B-$r.T)
$g=[Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($r.L,$r.T,0,0,$bmp.Size)
$bmp.Save("$D\shots\$Name.png"); $g.Dispose(); $bmp.Dispose()
Get-Process | ?{$_.MainWindowTitle -like "*$Name*"} | Stop-Process -Force -ErrorAction SilentlyContinue; Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
"saved $Name $($r.R-$r.L)x$($r.B-$r.T)"
