<?php
$path = "http://".$_SERVER['HTTP_HOST'];
$str = file_get_contents($path.'/config.json');
$config = json_decode($str, true);
$current = false;
$index_current = -1;
for($i=0;$i<sizeof($config['element']);$i++)  {
  $entry = $config['element'][$i];
  if (strpos($_SERVER["PHP_SELF"],$entry['url']) !== false) {
    $current = $entry;
    $index_current = $i;
  }
}
?>
  <style type="text/css">
    .block {
      /*min-height: 100px;*/
      padding-top: 15px;
        padding-bottom: 15px;
    }
  </style>
<div class="navbar navbar-info navbar-fixed-top shadow-z-1">
  <div class="navbar-header">
    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-responsive-collapse">
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
    </button>
    <a class="navbar-brand" href="<?php echo $path ?>"><i class="mdi-action-home"></i> GoGo<?php //if($current){ echo " | ".$current['label']; } ?></a>
  </div>
  <div class="navbar-collapse collapse navbar-responsive-collapse">
    <ul class="nav navbar-nav">

      <?php for($i=0;$i<sizeof($config['element']);$i++)  {
        $entry = $config['element'][$i];
        ?>
        <li <?php if($index_current == $i){ echo 'class="active"'; } ?>>
          <a href="<?php echo $path.$entry['url'] ?>"><i class="<?php echo $entry['icon']; ?> hidden-sm"></i><?php echo $entry['label']; ?></a>
        </li>
      <?php } ?>
    </ul>
  </div>
</div>
<div class="visible-lg" style="height:80px;"></div>
<div class="hidden-lg" style="height:70px;"></div>