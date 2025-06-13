<?php
require_once '../private/session_manager.php';

if (isset($_POST['inputUsername']) && isset($_POST['inputPassword'])){
    $username = $_POST['inputUsername'];
    $password = $_POST['inputPassword'];
    
    $login_status = login($username, $password);
    //echo $login_status;
    if($login_status == true){
        header('Location: index.php');
    }
} else 
    logout();

?>


<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>RAPTOR</title>
    <link href="./css/theme.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">

    <style>
        body {
            background: linear-gradient(135deg, #121212 0%, #1a1a1a 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
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
        
        .form-group label {
            color: #ffffff;
            font-weight: 500;
        }
        
        .form-control {
            background-color: #1e1e1e;
            border: 1px solid #2a2a2a;
            color: #ffffff;
            border-radius: 6px;
            padding: 12px;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            border-color: #00ff9d;
            box-shadow: 0 0 0 2px rgba(0, 255, 157, 0.2);
            background-color: #252525;
        }
        
        .btn-default {
            background-color: #00ff9d;
            color: #000000;
            border: none;
            padding: 12px 30px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-radius: 6px;
            transition: all 0.3s ease;
        }
        
        .btn-default:hover {
            background-color: #00ffcc;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 255, 157, 0.3);
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
    <div class="row" style="margin-top: 60px;">
        <div class="col-md-6 col-lg-offset-3">
            <div class="well">
                <form class="form-horizontal" action="login.php" method="POST" autocomplete="off">
                    <fieldset>
                        <legend>Welcome Attacker</legend>
                        <div class="form-group">
                            <label for="inputUsername" class="col-lg-3 control-label">Username</label>
                            <div class="col-lg-8">
                                <input class="form-control" id="inputUsername" name="inputUsername" placeholder="Enter your username" type="text" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="inputPassword" class="col-lg-3 control-label">Password</label>
                            <div class="col-lg-8">
                                <input class="form-control" id="inputPassword" name="inputPassword" placeholder="Enter your password" type="password" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="col-lg-8 col-lg-offset-3">
                                <button type="submit" class="btn btn-default btn-block">Login</button>
                            </div>
                        </div>
                    </fieldset>
                </form>
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
