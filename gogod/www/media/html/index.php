<?php

/*--------------------------------------------------------------------
Description:	Listing all file in folder "html"
, include javascript file to the html when display
Authors:		Marutpong Chailangka
Created:		2015-04-15
Updateed:       2015-08-04
                2015-08-18
                2015-09-07
                2015-10-10
---------------------------------------------------------------------*/


/*--------------------------------------------------------------------
 *
 * Declare variables and functions
 *
 *--------------------------------------------------------------------*/

$dir    = './';
$include_to_file = '<script src="../../bootstrap-material-design/dist/jquery-1.11.min.js"></script>'
.'<script src="../../dist/js/reconnecting-websocket.min.js"></script>'
.'<script src="../../dist/js/webui_event_handle.js"></script>';
$include_meta = '<meta  name = "viewport" content = "initial-scale = 1.0, maximum-scale = 1.0, user-scalable = no, minimal-ui"><meta charset="utf-8"/>';

/* Check is a html file by path */
function isHtml($file){
    $file_ext =  strtolower(substr($file, strrpos($file, '.') + 1));
    if(is_file($dir.$file) && strpos($file_ext, "htm")>-1){
        return true;
    }
    return false;
}

/* Getting content of a file */
function getFileContent($path){
    $myfile = fopen($path, "r");// or die("Unable to open file!");
    $content =  fread($myfile,filesize($path));
    fclose($myfile);
    return $content;
}

/* Getting title from a html file */
function getHtmlTitle($path) {
    $title = "Untitled";
    $fp = getFileContent($path);
    if (!$fp)
        return $title;

    $res = preg_match("/<title>(.*)<\/title>/siU", $fp, $title_matches);
    if (!$res)
        return $title;

// Clean up title: remove EOL's and excessive whitespace.
    $title = preg_replace('/\s+/', ' ', $title_matches[1]);
    $title = trim($title);

    if ($title == "title"){
        return getHtmlTitleJQuery($path);
    }
    return $title;
}

/* Getting title from a jQuery UI html file */
function getHtmlTitleJQuery($path) {
    $title = "Untitled";
    $fp = getFileContent($path);
    if (!$fp)
        return $title;

    $res = preg_match("/data-title=\"(.*)\"/siU", $fp, $title_matches);
    if (!$res)
        return $title;

    // Clean up title: remove EOL's and excessive whitespace.
    $title = preg_replace('/\s+/', ' ', $title_matches[1]);
    $title = trim($title);
    return $title;
}

/* Check the parametors First. */
if (isset($_GET['page']) && is_file($dir.$_GET['page']) && isHtml($_GET['page']) ) {
    $page = $_GET['page'];
    $lines = file($dir.$page);
    $fileContent = getFileContent($dir.$page);

    /* insert the code in the file content */
    if (strpos($fileContent,"<head>")>-1){
        $position = strpos($fileContent,"<head>")+6;
        $fileContent = substr_replace($fileContent, $include_meta, $position, 0);
    }

    if (strpos($fileContent,"</body>")>-1){
        $position = strpos($fileContent,"</body>");
        $fileContent = substr_replace($fileContent, $include_to_file, $position, 0);
    }

    echo $fileContent;

} else if (!isset($_GET['page'])) {
    $list_files = array();//scandir($dir,1);
    $exclude_files  = array(".", "..", "index.php", "event_handle.js");
    $files = scandir($dir);

    /* Listing html files in the folder */
    foreach($files as $file)
    {
        $file_ext =  strtolower(substr($file, strrpos($file, '.') + 1));
        if(is_file($dir.$file) && strpos($file_ext, "htm")>-1){
            array_push($list_files, $file);
        }
    }

    /* Exclude the specific files. */
    $list_files = array_diff ( $list_files , $exclude_files);

?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Web UI Files</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="author" content="Marutpong Chailangka">
    <link href="../../bootstrap-material-design/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="../../bootstrap-material-design/dist/css/material-fullpalette.min.css" rel="stylesheet">
</head>
<body>

    <?php include("../../www/include_header.php"); ?>
    <div class="container">
        <div class="panel panel-primary">
            <div class="panel-body">

                <h1 class="text-info visible-lg">Web UI Files</h1>
                <h3 class="text-info hidden-lg">Web UI Files</h3>

                <p class="text-muted">Currently only buttons, sliders, switches are supported. Their values can be accessed via default keys "button", "slider" and "switch"</p>
                <?php /* <p class="text-muted">Online UI Builder avaliable at <a href="https://01.org/rib/online/" target="_blank">https://01.org/rib/online/</a>
                    or on Raspberry Pi at <a href="<?php echo $path."/www/rapid_interface_builder" ?>" target="_blank"><?php echo $path."/www/rapid_interface_builder" ?></a></p> */ ?>
                    <br>

                    <div class="row">
                        <div class="col-lg-8 col-lg-offset-2">
                            <div class="bs-component">
                                <div class="list-group">
                                    <a href="<?php echo $path."/www/rapid_interface_builder" ?>" target="_blank" class="visible-lg visible-md">
                                        <div class="list-group-item">
                                            <button class="btn btn-fab btn-raised btn-sm btn-success"> <i class="mdi-content-add"></i></button>
                                            <div class="row-content">
                                                <h4 class="list-group-item-heading text-success"><p class="text-success">&nbsp;&nbsp;New File</p></h4>
                                            </div>
                                        </div>
                                    </a>
                                    <div class="list-group-separator"></div>

                                    <?php foreach ($list_files as $entry) {
                                        $html_file_path = $dir.$entry;
                                        $title = getHtmlTitle($html_file_path);
                                    ?>
                                    <a href="?page=<?php echo $entry ?>" target="_blank">
                                        <div class="list-group-item">
                                            <div class="row-action-primary">
                                                <i class="mdi-editor-insert-drive-file btn-info"></i>
                                            </div>
                                            <div class="row-content">
                                                <div class="col-lg-11 col-md-10" >
                                                    <h4 class="list-group-item-heading"><?php echo $entry ?></h4>
                                                    <p class="list-group-item-text"><?php echo $title  ?></p>
                                                </div>
                                                <div class="col-lg-1 col-md-2 visible-lg visible-md" >
                                                    <a  href="<?php echo $path; ?>/www/rapid_interface_builder/?importjson=<?php echo explode(".htm", $entry)[0];?>"
                                                        target="_blank"
                                                        class="btn btn-default btn-fab btn-raised btn-sm mdi-editor-mode-edit"
                                                        alt="Edit">
                                                    </a>
                                                </div>



                                            </div>
                                        </div>
                                    </a>
                                    <div class="list-group-separator"></div>
                                    <?php } ?>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="../../bootstrap-material-design/dist/jquery-1.11.min.js"></script>
        <script src="../../bootstrap-material-design/dist/js/bootstrap.min.js"></script>
        <script src="../../bootstrap-material-design/dist/js/material.min.js"></script>
    </body>
    </html>

<?php } ?>
