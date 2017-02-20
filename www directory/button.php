<?php

$host="localhost"; // Host name 
$username="root"; // Mysql username 
$password="raspberry"; // Mysql password 
$db_name="raspberry"; // Database name 
$tbl_name="notification"; // Table name 

// Connect to server and select databse.
mysql_connect("$host", "$username", "$password")or die("cannot connect"); 
mysql_select_db("$db_name")or die("cannot select DB");

// update data in mysql database 
$sql="UPDATE $tbl_name SET nb_n=nb_n+1 WHERE id='1'";
$result=mysql_query($sql);

?>

