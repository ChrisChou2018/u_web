// 一些公共的函数

var loadIframe = null;
function createIframe(){
    var iframe = document.createElement("iframe");
    iframe.style.cssText = "display:none;width:0px;height:0px;";
    document.body.appendChild(iframe);
    loadIframe = iframe;
}

function fBrowserRedirect(href, callbackTime){
    if (href != "") {
        if (navigator.userAgent.toLowerCase().match(/android/i) == "android") {
            createIframe();
            loadIframe.src = href;
        } else {
            window.location.href = href;
        }
    }
    var timer = setTimeout(function () {
        clearInterval(timer);
        window.location.href="http://a.app.qq.com/o/simple.jsp?pkgname=com.meimarket.activity#opened";
    }, callbackTime);
}

function errorMsg(message, time) {
    $(".m-toast").css("display", "block");
    $(".errText").html(message);
    setTimeout('$(".m-toast").css("display", "none");', time);
}

function getUrlParam(param) {
  var reg = new RegExp("(^|&)" + param + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
  var r = window.location.search.substr(1).match(reg);  //匹配目标参数
  if (r != null) {
      return unescape(r[2]); //返回参数值
  } else {
      return null;
  }
}

function is_login() {
    var ret;
    $.ajax({
        type: "GET",
        async: false,
        url: "/member",
        data: {_xsrf: getCookie("_xsrf")},
        dataType: "json",
        success: function(data) {
            if (data["result"] == "success"){
                ret = true;
            } else {
                ret = false;
            }
        },
        error: function() {
            ret = false;
        }
    });
    return ret;
}