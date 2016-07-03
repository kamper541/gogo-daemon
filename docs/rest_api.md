REST API
-------

### Key-Value


	GET /api/keyvalue/:key/:value
	
### Data Logging

 - List log file

	```
	GET /api/datalog/list
	```
	Response
		
	```json
	{
	  "data": [
	    "temperature",
	    "light"
	  ],
	  "result": true
	}
	```
 - Getting log


	Getting JSON format of log values by *filename* followed by `.json`
	```
	GET /api/datalog/get/:filename.json
	```
Response
	```json
{
	  "data": [
	    {
	      "field2": 4,
	      "created_at": "2016-07-02 18:33:01.107200"
	    },
	    {
	      "field2": 5,
	      "created_at": "2016-07-02 18:33:06.106856"
	    },
	    {
	      "field2": 6,
	      "created_at": "2016-07-02 18:33:11.111295"
	    }
	  ],
	  "result": true
}
	```

	Getting RAW format (like a .csv file) of log values
	
	```
	GET /api/datalog/get/:filename
	```
Response
	```json
	{
	  "data": "2016-05-09 18:27:16.000820,174\r\n2016-05-09 18:27:16.672749,175\r\n2016-05-09 18:27:17.503467,174\r\n2016-05-09 18:27:19.006473,174\r\n",
	  "result": true
}
	```
	

 - Adding a record
	```
	POST /api/datalog/new
	
	name={:name}&value={:value}
	```
Response
	```json
	{
	  "result": true
	}
	```
 - Delete the log by given a name

	```
	GET /api/datalog/delete/:filename
	```
Response
	```json
	{
	  "result": true
	}
	```

### Add-Ons
 - List the add-ons 

	```
	GET /api/addons/list
	```
Response
	```json
{
	  "data": ["default.py",  "telegrambot.py"],
	  "result": true
}
	```


 - Getting the add-ons content

	```
	GET /api/addons/get/:filename
	```
	It will return the python file (.py)


 - Validate a python file by name

	```
	GET /api/addons/verify/:filename
	```
Response
	```json
{
	  "result": true,
	  "error": ""
}
	```

 - Getting activation status verification each file

	```
	GET /api/addons/setting
	```
Response
	```json
{
      "data": {
        "default.py": 
	        {
	           "active": false,
	           "verify": true
	         },
		"telegrambot.py": 
            {
               "active": false,
               "verify": true
	        }
      },
	  "result": true
}
	```

 - Active or Deactive the add-ons

	```
	POST /api/addons/setting
	Content-Type: application/x-www-form-urlencoded
	Content-Length: {len}
	
	filename={:filename}&active={true|false}
	
	```
	Response : return the *activation or deactivation status* and *runnnig status*
	```json
{
	  "start": {
	    "result": true,
	    "error": ""
	  },
	  "result": true
	}
	```

 - Uploading a file
		
	**confirm** is a confirm of overwritten if a file has exists.
		
		
		
	```
	POST /api/addons/new
	Content-Type: Content-Type:multipart/form-dat
	Content-Length: {len}
	
	confirm={true|false}&file={file information & file content}
	
	
	```
Response : 	return the *upload status* and *error message*
	```json
{
	  "message": "file_exists",
	  "result": false
}
	```
