<?php
$path = "http://".$_SERVER['HTTP_HOST'];
$path_ip = str_replace(":8889",":8888",$path);
header("Location: ".$path_ip);
die();
?>