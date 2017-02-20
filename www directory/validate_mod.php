<?php
$host="localhost"; // Host name
$username="root"; // Mysql username
$password="raspberry"; // Mysql password
$db_name="raspberry"; // Database name

	$id=$_POST['ID'];
	$name=$_POST['name'];
	$nb_visits=$_POST['nb_visits'];
	$last_visit=$_POST['last_visit'];
	mysql_connect($host,$username,$password);
	mysql_select_db($db_name);
	$sql="SELECT folder FROM visitors WHERE ID =".$id;
	$result=mysql_query($sql);
	while($rows=mysql_fetch_array($result))
		$path=$rows['folder'];
	$sql= "UPDATE visitors SET name='".$name."', nb_visits='".$nb_visits."', last_visit='".$last_visit."' WHERE ID =".$id;	
	system("sudo python create_name.py ".$path." ".$name);
	$resultat = mysql_query($sql) or die ('Erreur SQL !'.$sql.'<br />'.mysql_error());
	if ($resultat) 
	{	 
		echo '<script language="javascript">alert("Modification done with success");</script>';
		mysql_close();
	} 
	else 
	{ 
		echo '<script language="javascript">alert("ERROR while modifying the entry");</script>';  
	} 
	header("Location: dynamic_table.php");
?>