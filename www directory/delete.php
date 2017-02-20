<?php
$host="localhost"; // Host name
$username="root"; // Mysql username
$password="raspberry"; // Mysql password
$db_name="raspberry"; // Database name
$id=$_POST['ID'];
	
mysql_connect($host,$username,$password);
mysql_select_db($db_name);
$sql="SELECT folder FROM visitors WHERE ID =".$id;
$result=mysql_query($sql);
while($rows=mysql_fetch_array($result))
	$path=$rows['folder'];
$del='sudo python delete_visitor.py '.$path;
	system($del);
	$sql= "DELETE FROM visitors WHERE ID =".$id;	
	$resultat = mysql_query($sql) or die ('Erreur SQL !'.$sql.'<br />'.mysql_error());
	if ($resultat) 
	{	 
		echo '<script language="javascript">alert("Suppression aboutie");</script>';
		mysql_close();
	} 
	else 
	{ 
		echo '<script language="javascript">alert("Suppression non aboutie");</script>';  
	} 
	header("Location: dynamic_table.php");
?>
