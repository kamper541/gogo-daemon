<?php
//var_dump($argv);

$rijnKey = "\x1\x2\x3\x4\x5\x6\x7\x8\x9\x10\x11\x12\x13\x14\x15\x16";
$rijnIV = "\x1\x2\x3\x4\x5\x6\x7\x8\x9\x10\x11\x12\x13\x14\x15\x16";

function fnEncrypt($s){
	global $rijnKey, $rijnIV;

// Have to pad if it is too small
	$block = mcrypt_get_block_size(MCRYPT_RIJNDAEL_128, 'cbc');
	$pad = $block - (strlen($s) % $block);
	$s .= str_repeat(chr($pad), $pad);

	$s = mcrypt_encrypt(MCRYPT_RIJNDAEL_128, $rijnKey, $s, MCRYPT_MODE_CBC, $rijnIV);
	$s = base64_encode($s);
	$s = str_replace("+", "BIN00101011BIN", $s);
	return $s;
}


$return = array("result"=>false);
if (isset($_POST['raspberry-pi'])){
	$setting_file = "../raspberry_setting.json";
	$key_pushbullet = "pushbullet_token";
	$key_gmail_user = "gmail_username";
	$key_gmail_pass = "gmail_password";
	$key_clouddata_key = "clouddata_key";

	$jsonString = file_get_contents($setting_file);
	$data = json_decode($jsonString,true);
	if (isset($_POST["inputToken"]) && strlen($_POST["inputToken"])==34){
		$data[$key_pushbullet] = $_POST["inputToken"];
	}

	if (isset($_POST["inputCloudDataKey"]) && strlen($_POST["inputCloudDataKey"])==16){
		$data[$key_clouddata_key] = $_POST["inputCloudDataKey"];
	}
	
	if (!empty($_POST['input_gmail_username']) && !empty($_POST['input_gmail_password'])){
      $data[$key_gmail_user] = $_POST["input_gmail_username"];
      $data[$key_gmail_pass] = fnEncrypt($_POST["input_gmail_password"]);
	}

	//Encode to JSON and Save to config file.
	$newJsonString = json_encode($data);
	$result = file_put_contents($setting_file, $newJsonString);
	$return['result'] = (!$result===false);
}

echo json_encode($return);

?>