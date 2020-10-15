<?php

$servername = "localhost";
// REPLACE with your Database name
$dbname = "e_meter";
// REPLACE with Database user
$username = "root";
// REPLACE with Database user password
$password = "";

// Keep this API Key value to be compatible with the ESP32 code provided in the project page. 
// If you change this value, the ESP32 sketch needs to match

$meter_id = 1001;
$voltage = 123;
$current = 123;
echo "meter_id: ".$meter_id;
echo "voltage: ".$voltage;
echo "current: ".$current;

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

//$sql = "INSERT INTO test (meter_id, voltage, current) VALUES ('" . $meter_id . "', '" . $voltage . "', '" . $current . "')";
$sql="INSERT INTO test (meterId,voltage,current) VALUES('$meter_id','$voltage','$current')";

if ($conn->query($sql) === TRUE) {
    echo "New record created successfully";
} 
else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}
$conn->close();

function test_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}