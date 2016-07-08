Installation
===================



**Install by Package**

```bash
$ sudo apt-get update
$ wget https://git.learninginventions.org/gogo/gogod/raw/master/package/gogod_2.0.0-14.deb
$ sudo dpkg -i gogod_2.0.0-14.deb
```

> **Note:** if you got a problem like this
> 
> ![enter image description here](https://git.learninginventions.org/gogo/gogod/raw/master/docs/images/installation/install_error.png)

then run a command to complete the installation

```bash
$ sudo apt-get install -f
```

**Install by Image File**

 - Download the ZIP file of Image (<a href="https://gogo.learninginventions.org/download/#raspberrypi" target="_blank">download</a>)
 - After downloading the .zip file, unzip it to get the image file (.img)
 - Insert SD Card into SD Reader
 - Using  Win32DiskImager  ([download](https://sourceforge.net/projects/win32diskimager/)) 
	 - Select the Image File (.img) 
	 - Choose the drive letter that is assigned to the SD Card such as <kbd>F:</kbd>
	 - Click **Write**
	 
	    ![Win32DiskImager](https://git.learninginventions.org/gogo/gogod/raw/master/docs/images/installation/win32diskimager.png)
