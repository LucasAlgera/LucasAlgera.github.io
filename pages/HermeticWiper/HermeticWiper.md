# Hermetic Wiper

Hermetic wiper is known to have done a lot of damage to Ukrainian infrastructure in the Russia Ukraine war.  
It was first seen February 2022, hours before the Russian invasion of Ukraine and mostly targeted governmental, financial and defense infrastructure. 


## File information
The file icon is a present, which could be intentional. But it is also  the standard image for a Visual Studio GUI project, though it's still somewhat fitting.  
![present](/assets/images/Hermetic/image-11.png)  

The file is **signed** with a stolen signature from Hermetica Digital Ltd, hence the name Hermetic Wiper.   
![signature](/assets/images/Hermetic/image-12.png)  

**File name:** c.exe   
**SHA-256:** 1bc44eef75779e3ca1eefb8ff5a64807dbc942b1e4a2672d77b9f6928d292591  
**File size:** 117.000 bytes
**Language:** C/C++

## epmntdrv.sys
Hermetic uses a technique called Bring Your Own Vulnerable Driver (BYOVD) to get direct access to a disk while bypassing Windows security features. 
 
Epmntdrv.sys is a legitimate signed kernel driver created for EaseUS Partition Master. The partition manager required direct access to the disk. This feature was abused by Hermetic.  

Inside the driver we see that the driver registers itself as `"EPMNTDRV"`.  
![EPMNTDRV](/assets/images/Hermetic/image-15.png)

Here we see that the driver searches in the specified harddisk for the linked driver, being disk.sys. Epmntdrv.sys sends all its incoming requests directly to that driver.   
![disk.sys](/assets/images/Hermetic/image-16.png)

Both `IRP_MJ_READ` and `IRP_MJ_WRITE` get directly passed to lower level drivers in the kernel.  
![READ](/assets/images/Hermetic/image-17.png)
![WRITE](/assets/images/Hermetic/image-18.png)

Normally there are restrictions to writing to boot sectors, direct writes to partitions, etc. But since this driver is used for a partition manager, this was not needed. This way Hermetic can both access disk and bypass many Windows security features. 


## Hermetic's Setup
Hermetic requires to be run in administration mode. Before getting to the wiping, some setup is required. 

### Setting Privilege Tokens
Hermetic tries retrieve the Privileges of both "SeBackupPrivilege" and "SeShutdownPrivilege". There seems to be a check on the filename which impacts the building of the strings. The "SeShutdownPrivilege" string starts as "SeShutdo....ivilege", if the filename starts with a `"c"`, the missing `"wnPr"` will be added. If not the LastStatus is filled with this error code: ` C0000060 (STATUS_NO_SUCH_PRIVILEGE)`.  

`LookupPrivilegeValueW("SeShutdo....ivilege")`  
`LookupPrivilegeValueW("SeBackupPrivilege")`

![alt text](/assets/images/Hermetic/image-10.png)

Hermetic uses `AdjustTokenPrivileges()` to apply the settings.


### Extracting epmntdrv.sys
The earlier discussed driver sits compressed inside of RT_RCDATA (a section inside of .rsrc).  
It uses `VerifyVersionInfoW()` to specify the version of the OS and uses `IsWow64Process()` to specify the current hardware architecture. This is needed to load the correct version of the driver to disk, it brings along  the following versions:  
- **Resource:** "DRV_XP_X86" -- **MD5:** eb845b7a16ed82bd248e395d9852f467
- **Resource:** "DRV_XP_X64" -- **MD5:** 095a1678021b034903c85dd5acb447ad
- **Resource:** "DRV_X86" -- **MD5:** a952e288a1ead66490b3275a807f52e5
- **Resource:** "DRV_X64" -- **MD5:** 231b3385ac17e41c5bb1b1fcb59599c4

![resources](/assets/images/Hermetic/image-2.png)  

After knowing which architecture to load in the driver, Hermetic searches the correct driver version inside of its resources using `FindResourceW(driverBuffer, "DRV_X64", RCDATA)`.  

`RegOpenKeyW` is used to set `"CrashDumpEnabled"` inside of `"SYSTEM\\CurrentControlSet\\Control\\CrashControl"` to false. This is also a commodity in many ransomware cases. Disabling this setting makes sure no memory dump gets created when the OS hits a bluescreen. 

Hermetic checks whether the epmntdrv.sys driver is already present and running on the device by trying to open `EPMNTDRV\\0`, this would be the instance of EPMNTDRV running on the main disk. The handle is retrieved by calling `CreateFileW("\\\\.\\EPMNTDRV\\0", ...)`.  
If the handle returned is invalid, hermetic continues the installation. 

Hermetic **creates a new file** inside of `C:\\Windows\\system32\\Drivers\\`. A 4-letter filename is randomly generated using the current PID and the .sys extension is added.  

Before **making the driver a service**, Hermetic checks its `"SeLoadDriverPrivilege"` privilege using LookupPrivilegeValueW. If this privilege is not set, it adjusts this privilege using AdjustTokenPrivileges.   
After this a new service is created for this driver and finally hermetic deletes the following key `"SYSTEM\\CurrentControlSet\\services\\<generated_name>.sys"` using RegDeleteKey. This might have been done to remove any traces of this driver having been present. 


### Disabling VSS
The VSS service is opened using `OpenSCManagerW` and `OpenServiceW`.  
Volume Shadow Copy Service (VSS) is a Windows service used for creating snapshots of data and making sure backups are in place. Hermetic disables this service using `ChangeServiceConfigW`.  
![ChangeServiceConfigW](/assets/images/Hermetic/image-1.png)


## Wiping
A lot of wipers try to brute force their way through the data. Zeroing out everything, encrypting all files in a system, etc. This creates a lot of "noise" inside of the OS which makes detection easier and takes a lot of time and resources to do.  
Hermetic takes a more surgical approach. It targets vital structures inside of file systems and takes advantage of disk fragmentation to make the retrieval of the original structure near impossible. This approach is way less loud and gets done in no time. 


### Step 1 - Data enumeration
**Enumerating Files**   
Hermetic starts by enumerating through every disk on the device. It goes through important structures and files inside of the disks using it's direct access gained from the vulnerable driver.  

`DeviceIoControl` is used to send control codes directly to the driver. `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS` and `FSCTL_GET_RETRIEVAL_POINTERS` are used to map out specific files on disk, making sure fragmentation is taken into account.   
![deviceiocontrol](/assets/images/Hermetic/image-3.png)

**Enumerating Drives**   
Hermetic loops through max 101 drives a and tries to get a valid handle to the drive. 
![drive looping](/assets/images/Hermetic/image-7.png)  
The control code `IOCTL_DISK_GET_DRIVE_LAYOUT_EX` is used by the malware to get more information about drive partitions.  
The wiper rapidly moves through the drive by jumping through all the partitions using `SetFilePointerEx`. The data in the partition is read using `ReadFile`. Both the data and the raw positions of the partitions are sent to a function which populates a wipe struct. 
![disk enumeration](/assets/images/Hermetic/image-6.png)

**Prepping random buffers**  
After knowing the raw geometry of the files/structures. Hermetic prepares a buffer which it eventually uses to override that part of the disk. The buffer gets filled with cryptographically random values, and if that fails it falls back to zeroing out the buffer.  
![random buffer](/assets/images/Hermetic/image-4.png)

**List of enumerated data**
- Itself, Hermetic makes sure it makes itself untraceable. 
- Every single disk's partitions. 
- `C:\\System Volume Information\`, this folder contains System Restore points, Volume Shadow Copies, and search indexing databases. 
- `$LogFile` and `$Bitmap`, critical internal metadata files of the NTFS file system.
- `ntuser.dat`, critical Windows registry hive file that stores user-specific settings.
- Every file under `"\\\\?\\C:\\Documents and Settings"` (C:\Users) that is > 1KB and is a `FILE_ATTRIBUTE_REPARSE_POINT` (symbolic link, junction, mount point). 
- Every file under `"\\\\?\\C:\\Windows\\System32\\winevt\\Logs"`. 
- MFT and MFT-mirror, the malware will wipe these files. Without these files, recovery of files using NTFS will become way harder.


### Locking drives
`FSCTL_LOCK_VOLUME`: Prevents new opens and locks the volume for exclusive access.  
`FSCTL_DISMOUNT_VOLUME`: Dismounts the filesystem from the volume.  
![locking files](/assets/images/Hermetic/image-8.png)

### Creating more fragmentations
Using the `FSCTL_MOVE_FILE`, Hermetic makes a bunch more fragmentations inside of the following folders:  
![things to fragment](/assets/images/Hermetic/image-9.png)

The fragmentation flow looks as follows:

![ret pointer](/assets/images/Hermetic/image-13.png)  
`FSCTL_GET_RETRIEVAL_POINTERS` is used to get the bounds of a file, this data is then fed into `FSCTL_MOVE_FILE` to create fragmentations inside that file.  
![fragment](/assets/images/Hermetic/image-14.png)


### Filling partitions with garbage 
Near the end Hermetic loops over all the collected data in the wiper structs. These structs contain both positions of partitions in the drive and the random generated buffer to fill that partition with.   
Using `WriteFile`, the wiper overrides a part of the partition. And `SetFilePointerOffsetEx` is used to move through the saved positions in the drives. 

## Conclusion
Hermetic does not rely on encrypting data or wiping entire disks. It uses the underlying file management system against itself by overriding important structures within that system, creating even more fragmentation and eventually deleting the MFT which holds everything together.  
It uses a vulnerable drive to bypass a lot of Windows security features and to get direct access to the drives.  

Having run the wiper, the end result is the following:  
![end result](/assets/images/Hermetic/image-19.png)

### IOC's
- `"SYSTEM\\CurrentControlSet\\services\\<generated_name>.sys"`
- `"C:\\Windows\\system32\\Drivers\\<generated_name>.sys"`

### MITRE ATT&CK mapping

| ID| Meaning|
| --------- | ------- |
| T1082     | System Information Discovery|
| T1012     | Query Registry|
| T1543.003 | Create or Modify System Process: Windows Service|
| T1068     | Exploitation for Privilege Escalation *(BYOVD)*|
| T1561.001 | Disk Wipe|
| T1561.002 | Disk Structure Wipe|
| T1005     | Data from Local System|
