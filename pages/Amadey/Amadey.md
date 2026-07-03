# Part 1 - Amadey

Amadey is a well known loader and infostealer and is operated as a MaaS. It has been running since at least 2018 and has recently been taken down by law enforcement in June 2026.  
In this part 1 I will go into how Amadey works, steals and loads. 

**MITRE ATT&CK mapping**
| ID | Meaning |
|---|---|
|T1027.007| Obfuscated Files or Information: Dynamic API Resolution|
|T1555.003 | Credentials from Web Browsers|
|T1082 | System Information Discovery|
| T1012 | Query Registry |
| T1005 | Data from Local System |
| T1071 | Application Layer Protocol| 
| T1140 | Deobfuscate/Decode Files or Information| 
| T1041 | Exfiltration Over C2 Channel | 
| T1547 | Boot or Logon Autostart Execution|

**Language:** C/C++  
**Mutex**: CzBbrPKHpcNWzWL  
**RC4 key**: izesamgdxiur  
**BuildID**: Crypt  

### Resolving API and strings
First thing Amadey does is it's string resolving. It uses a simple XOR algorithm for this.  
![alt text](/assets/images/Amadey/image.png)

After the resolving we get the following API's:   
```
GlobalAlloc, GlobalLock, GlobalUnlock, GlobalFree, Sleep, CreateToolhelp32Snapshot, VirtualAllocEx, WriteProcessMemory, GetTempPathA, GetVolumeInformationA, GetVersionExA, CreateFileA, WriteFile, CloseHandle, GetModuleFileNameA, MoveFileExA, VirtualAlloc, CreateThread, WaitForSingleObject, VirtualFree, GetNativeSystemInfo, CreateDirectoryA, CreateProcessA, CopyFileA, lstrlenA, lstrcpyA, lstrcatA, lstrlencpyA, SetFileAttributesA, CreateMutexW, OpenMutexW, ReleaseMutex, GetUserNameA, GetUserNameW, GetComputerNameW, CryptAcquireContextA, CryptGenRandom, CryptReleaseContext, GetCurrentHwProfileA, InternetOpenA, InternetConnectA, HttpOpenRequestA, HttpSendRequestA, InternetReadFile, InternetCloseHandle, InternetOpenUrlA, ShellExecuteA, SHGetFolderPathA, wsprintfA.
```

After this the mutex name `CzBbrPKHpcNWzWL` gets resolved using the same XOR algorithm.  
This name is used to check whether there is already another instance of this mutex running, if there is the malware exits. 

### Setup
Finally the malware will check whether it's being run from the `C:/Programdata` folder. If not, the malware copies itself into this directory using `CopyFileA()`.  
A 5 letter random name is generated using `CryptGenRandom()`, in this case the file `xfpbr.exe` was made. 

The file is thereafter set as a value in the Run key (`"Software\\Microsoft\\Windows\\CurrentVersion\\Run"`). To make sure the newly made file has persistence.

The file's attributes get set using `SetFileAttributesA()` using `FILE_ATTRIBUTE_HIDDEN` and `FILE_ATTRIBUTE_SYSTEM`. This marks the file as hidden and marks the file as used by the OS.

Finally this file is ran using `ShellExecuteA(0, "open", "xfpbr.exe")`.

### String decoding
Amadey decodes the following strings using the same XOR algorithm as before.  

![alt text](/assets/images/Amadey/<Screenshot 2026-07-03 184123.png>)

This time we get the following strings: 

| Decoded string | Actively used in this build? | 
| --- | --- |
| "62.60.226.159" | yes |
| "196.251.107.104" | yes |
| "/xvzpjyddlu/getdata.php" | yes |
|  "izesamgdxiur" | yes |
|  "Crypt" | yes |
|  _"HTTP/1.1\r\n" | no |
| _"Host:"| no |
|  "\r\nPragma: no-cache\r\nContent-type: text/html\r\nConnection:close\r\nUser-Agent: Mozilla/5.0 (Windows NT 100;Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome109.0.0.0Safari/537.3\r\n"| no |
| _"Content-Length:"| no |
| _"Transfer-Encoding"| no |
| _"HTTP/1.1_200_OK"| no |
| _"%d"| no |
| _"POST"| no |
| _"GET"| no |
| _"chunked" | no |

### Initial C2 Communication
Amadey spawns a new thread which handles all C2 communication.  
It starts by creating a user profile consisting of the following: 
- Username -> `GetUserNameA()`
- HWID -> `GetCurrentHwProfileA()`
- OS version -> `RtlGetVersion()`

This eventually comes down to 1 big string: 
`username=[username]&hwid={[12345678-abcd-1234-abcd-123456789abc]}&os=10`  
This data is then encrypted using an RC4 stream cipher algorithm. For this it uses the key: `"izesamgdxiur"`.

Amadey tries to make a HTTP POST request using `HttpOpenRequestA()` to 2 IP addresses. It first tries `62.60.226.159`, if that fails it tries `196.251.107.104`. Amadey then sends the encrypted data to `/xvzpjyddlu/getdata.php` over port 80.

The C2 posting logic looks fairly straight forward:  
![C2 posting](/assets/images/Amadey/<Screenshot 2026-07-03 190451.png>)

Within this function, Amadey also tries to retrieve some data from the server. This again goes via either `62.60.226.159` or `196.251.107.104` over `/xvzpjyddlu/getdata.php`. This RC4 encrypted data is a set of instructions given to Amadey by the C2 server. 


### Receiving commands
In this specific build, Amadey takes 3 commands:
1. **exe**:  
    This command retrieves a file from the server, makes it persistent and executes it.  

    Amadey uses `InternetReadFile()` to read a file from the server into a buffer. This buffer is eventually written to a file created in the `%Temp%` folder, again having a random name generated using `CryptGenRandom()`.  
    The file is executed using `ShellExecuteA(0, "open", [filename])`.  
    The file is made persistent using the windows Registry's Run key. 

2. **cmd**:  
    The cmd command directly executes a given command by using `CreateProcessA()`.   
    This would look something like this:  
    `CreateProcessA(0, "cmd.exe /c [given_command]", CREATE_NO_WINDOW)`. 

3. **updatedll**: This seems to be an unused feature in this build. No interesting things happen with this command. 


### Secondary plugins/payloads from C2
Using the commands specified above, Amadey has been known to drop off a couple of malicious secondary payloads: 
1. **cred64.dll:**   
    >This is the credential stealer module. It goes after passwords, cookies, and autofill data from web browsers (Chrome, Edge, Firefox), email clients, and FTP/SSH clients. It is also known to go after cryptocurrency wallets.

2. **clip64.dll:**   
    >This is the clipboard clipper module. It monitors the system clipboard for cryptocurrency wallet addresses. When a user copies an address, this DLL swaps it with an attacker-controlled address before the user pastes it, redirecting funds

3. **StealC:**  
    One of amadey's drops is known to be StealC. An interesting thing found in the case of these infostealers was that these two shared the same C2 infrastructure. This allowed law enforcement to simultaneously take them down.  

    View my StealC analysis [here](https://lucasalgera.com/?page=stealc/stealc).  
    Read more about the takedown here: 
    - https://www.politie.nl/nieuws/2026/juni/24/11-operatie-endgame-opnieuw-twee-infostealers-offline.html
    - https://www.microsoft.com/en-us/security/blog/2026/06/24/stealc-and-amadey-breaking-down-infostealers-and-the-cybercrime-services-that-deliver-them/



## IOC's 
| name | | | 
| --- | --- | --- |	
| C:\ProgramData\xfpbr.exe |	(SHA-256) 203858a2a480b9efc8e97209a38731941d985960eaa9fcf6045bb972f34b0761	|168.960 bytes |	
| SOFTWARE\Microsoft\Windows\CurrentVersion\Run | C:\ProgramData\xfpbr.exe | |
|62.60.226.159/xvzpjyddlu/getdata.php|||
|196.251.107.104/xvzpjyddlu/getdata.php|||
| Mutex name| CzBbrPKHpcNWzWL|||
| BuildID | Crypt |||