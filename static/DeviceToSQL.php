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
$api_key_value = "secret_key";

$api_key= $sensor = $location = $value1 = $value2 = $value3 = "";

if ($_SERVER["REQUEST_METHOD"] == "GET") {
    $api_key = test_input($_GET["api_key"]);
    // echo "api_key: ".$api_key;
    // echo "<br>";
    // $meter_id = test_input($_POST["meter_id"]);
    // $voltage = test_input($_POST["voltage"]);
    // $current = test_input($_POST["current"]);
    // echo "meter_id: ".$meter_id;
    // echo "<br>";
    // echo "voltage: ".$voltage;
    // echo "<br>";
    // echo "current: ".$current;
    // echo "<br>";
    if($api_key == $api_key_value) {                
        $meter_id = test_input($_GET["meter_id"]);
        $voltage = test_input($_GET["voltage"]);
        $current = test_input($_GET["current"]);
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
    }
    else {
        echo "Wrong API Key provided.";
    }
}
else {
    echo "No data posted with HTTP POST.";
}

function test_input($data) {
    echo "data: ".$data;
    echo "<br>";
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    
    return $data;
}