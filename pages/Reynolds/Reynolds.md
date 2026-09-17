# Reynolds Ransomware

Reynolds ransomware is a recently discovered piece of ransomware targeting Windows systems.  
It was first seen November 2025 and has only recently publicly been disclosed (February 2026).   

Reynolds is known for its BYOVD (Bring your own vulnerable driver) attack on the OS, targeting antivirus software. 

## 402.sys - NSecKrnl
This is the driver Reynolds brought along, it's sitting encrypted in the executable. 

402.sys (NSecKrnl) is a kernel-mode driver developed by **NSecsoft**. It was originally built for Endpoint Management (for IT administrators), employee monitoring software, etc.  
The vulnerability in this driver is tracked under [CVE-2025-68947](https://nvd.nist.gov/vuln/detail/cve-2025-68947).

In DriverEntry we see the driver registers itself as `NSecKrnl`. User-mode processes can communicate with the driver via the Symbolic Link it creates as `"\\DosDevices\\NSecKrnl"` which links to `"\\Device\\NSecKrnl"`.  

![DriverEntry](/assets/images/Reynolds/image-2.png)  

Interesting for us will be `IRP_MJ_DEVICE_CONTROL` (the IOCTL dispatcher). Opening the dispatcher we see that the driver handles four different IOCTL codes: 
- `0x2248D4` (IOCTL: Add specified PID to an array)
- `0x2248D8` (IOCTL: Remove specified PID from an array)
- `0x2248DC` (IOCTL: Queries info from process)
- `0x2248E0` (IOCTL: Terminate process using PID)

The last IOCTL code implements process termination. This function takes in a PID and gets the PEPROCESS structure of that PID using `PsLookupProcessByProcessId`. Using `ObOpenObjectByPointer` with the OBJ_KERNEL_HANDLE flag, the driver gets the direct handle to the specified process. Eventually that process is terminated using `ZwTerminateProcess`. No process verification is done inside of this function so calling this function can also terminate any SYSTEM level processes.  
![Terminate process](/assets/images/Reynolds/image-5.png)

The reason this driver is vulnerable is because this driver does not check who gets a handle to it. The Create/Close handle logic is as simple as this:   
``` c
__int64 __fastcall IRP_MJ_CLOSECREATE(__int64 a1, IRP *a2)
{
  a2->IoStatus.Status = 0;
  IofCompleteRequest(a2, 0);
  return 0;
}
```

Nor does the IOCTL dispatcher do any security checks. This way any process with elevated privileges can directly call kernel drivers, directly bypassing AV's. 

## Decrypting driver 
Reynolds stores an RC4 encrypted version **402.sys** inside of its .data section. It decrypts this buffer using the undocumented Advapi32.dll function `SystemFunction032()`.

**Encrypted driver data:**   
- SHA256 (encrypted): `9d4a2e46c9b9e63eb762f460717f29a1fc922679bb6dfc15f2b1568f2e8929c7`  
- Length: `0x61E0` | `25.056 bytes`

**RC4 key**  
Looking in memory right before the decryption we can see the RC4 key:  
![RC4 key](/assets/images/Reynolds/image.png)  
ASCII representation: `nK.}EY08ÕÀ.?.þ<e`  
HEX representation: `6E 4B 8E 7D 45 59 30 38 D5 C0 12 3F 8D FE 3C 65`

Running it shows us a PE file sitting in memory:  
![PE file](/assets/images/Reynolds/image-1.png)  

A new file is created with the following path: `L"C:\\ProgramData\\402.sys"` and the decrypted buffer is written to this file. 


## Loading the driver
After having decrypted the driver and having written it to disk we see that it tries to load the driver into the OS kernel.  
First, Reynolds checks its privilege tokens using `LookupPrivilegeValueW` with the value: `"SeLoadDriverPrivilege"`. If the privileges tokens don't match up, `AdjustTokenPrivileges` will be called to enable the correct tokens. 

Next, the registry is prepped for the driver to be loaded. A new key is created of `HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\` with the name of the driver. In here its Type, ErrorControl and Start and ImagePath(`"\??\C:\ProgramData\402.sys"`) is set. 

After the setup has been done, `NtLoadDriver` is called which loads the driver into memory.  
And when all is done, the originally created registry keys are removed to remain stealth. 

If something fails, `"faild to load driver ,try to run the program as administrator!!\n"` is printed to the screen and exits the program. Otherwise `"driver loaded successfully !!\n"` is printed. 

## Disabling AV
A handle to the driver is retrieved by calling CreateFileW with the symbolic link name the driver registered itself as:  
![retrieve handle](/assets/images/Reynolds/image-6.png)

Reynolds goes through a list of known antivirus process names. For every entry it calls `CreateToolhelp32Snapshot` and compares the names in that list to the names in its own blacklist. If it has found a match, the PID of that process is returned. 

![process filtering](/assets/images/Reynolds/image-7.png)

It's there we also see the vulnerable driver being used. An IOCTL code is sent to the driver using `DeviceIoControl`. It uses the same IOCTL code we saw triggering process termination in the driver (`0x2248e0`).

| Terminated Processes| | |
| --- | --- | --- |
| Sophos UI.exe |                               SymCorpUI.exe |cyrprtui.exe   |
| SEDService.exe |SISIPSService.exe |cyserver.exe |
| SophosHealth.exe   |SISIDSService.exe |cytool.exe |
| SophosFS.exe |SmcGui.exe |cytray.exe |
| SSPService.exe|sisipsutil.exe |cyuserserver.exe   |
| SophosFileScanner.exe |sepWscSv  |CyveraConsole.exe |
| McsAgent.exe |c64.exe |tlaworker.exe|
| McsClient.exe |MsMpEng.exe |ekrn.exe |
| SophosLiveQueryService.exe |CSFalconServ  |eguiProxy.exe   |
| SophosNetFilter.exe |ice.exe |egui.exe |
| SophosNtpService.exe   |cydump.exe |aswEngSrv.exe |
| hmpalert.exe |cyreport.exe   |aswidsagent.exe |
|  SophosOsquery.exe |cyrestart.exe | Sophos.Encryption.BitLockerService.exe  |
| AvastUI.exe | ccSvcHst.exe   |


## Discovering files/drives + IOCP
**File discovery**  
Reynolds targets all disk types except `DRIVE_CDROM` and unknown drive formats.  
Using `GetLogicalDrives` and `GetDriveTypeW` it loops through and filters through the drives. If a drive is of type `DRIVE_REMOTE`, `WNetGetConnectionW` is used to get the remote name of the drive. 

For every drive a readme file is made, e.g. for the C:\ drive: `"C:\\___RestoreYourFiles___.txt"`. This file contains instructions for the victim.  
![instructions](/assets/images/Reynolds/image-8.png)

Reynolds crawls through the filesystem by using API's like `FindFirstFileW` and `FindNextFileW`. It uses string comparisons to discover folders and to skip files. The following files are not taken into the encryption process: 
- any .exe, .dll or .sys file (for system stability)
- files that have the .locked extension
- more specific files in the [Appendix whitelist](#whitelisted-files)
- files containing `___RestoreYourFiles___.txt`  

*A brilliant way to stop ransomware attacks would be to call all your files `document___RestoreYourFiles___.txt.docx` :D*

**IOCP**  
Reynolds uses I/O Completion Port (IOCP) to massively speed up its encryption routine. Normally ransomware would waste an enormous amount of time retrieving file handles, opening files, encrypting, and writing/closing files. IOCP enables you to handle multiple asynchronous I/O operations with a higher speed. 

Reynolds spawns two IoCompletionports using `CreateIoCompletionPort`. Then every for every available processor (info retrieved by `GetSystemInfo`) two worker threads are spawned, all waiting for instructions given to it by monitoring its I/O Completion status using `GetQueuedCompletionStatus`.  
If no work is given to them, they too will discover files to encrypt. 

The worker thread's logic looks like this:  
![worker thread](/assets/images/Reynolds/image-9.png)

If a file is found that should be encrypted, an IOCP  request is made using `PostQueuedCompletionStatus`. This request contains the filepath of the to-be encrypted file. 


## Encryption routine
Early on in the executable CryptAcquireContextW got called to initialize AES:  
```c
CryptAcquireContextW(&phProv,NULL,NULL,PROV_RSA_AES, CRYPT_VERIFYCONTEXT);`
```

Within this AES context, for every file, a buffer is filled with a new cryptographically random series of bytes. Reynolds goes through some complex mathematical instructions and eventually fills a key-like buffer. 

Eventually the file is read and traversed through using `SetFilePointerEx`, encrypted and written back to. For me, going into the cryptography is a bit outside of scope, so I will stick to the OS-related things.  

If a file can't be opened due to being used in another running process, the Windows **Restart Manager library** is used to find out what process this is.   
`RmRegisterResources` and `RmGetList` are used to find out which PID has access to the requested file.  
When found `TerminateProcess` is called and the encryption routine is attempted again. 

Reynolds waits for all worker threads to finish their work using `WaitForMultipleObjects`. Once it's done it exits. 

## IOC
| Files | Hash (SHA-256) |
| --- | ---|
| reynolds.exe | 278593da28e45476a4a784af9841c5522a23aed62c14ce1ddba2b4ce5705c574|
| 402.sys (decrypted) | 206f27ae820783b7755bca89f83a0fe096dbb510018dd65b63fc80bd20c03261 |
| RestoreYourFiles.txt |c3bca7c9e5b0d3d9dadcae78ca79ee687c8f93d3e59500e86f03685d9ee4db70 |  

**onion address**: http[:]//bs2tlg32pfjwmclm22cyngqmoo24cdlhfxzbruwrdaxumisfeory32qd[.]onion  
**File extensions**: `.locked`  
**IOCTL-code used**: `0x2248E0`  
**Communication**: https[:]//qtox[.]github[.]io  
**Poison ID**: `6F7831EBB5EEB933275BD6F4B4AA888918E9B7E40454A477CADDE7EE02461153D3B77AE50798`  
**RC4 key**: `nK.}EY08ÕÀ.?.þ<e`

## Appendix

### Whitelisted files
| Whitelisted files |
|---|
|Tor Browser        |
|Internet Explorer|
|Google|
|Opera|
|Opera Software|
|Mozilla|
|Mozilla Firefox|
|Windows|
|Windows.old|
|$Recycle.Bin|
|ProgramData|
|All Users|
|autorun.inf|
|boot.ini|
|bootfont.bin |
|bootsect.bak|
|bootmgr|
|bootmgr.efi|
|bootmgfw.efi |
|ntldr|
|ntuser.dat|
|ntuser.dat.log|
|ntuser.ini|
|desktop.ini|
|iconcache.db |