// 存放一些公用的代码
function getUrlParam(param) {
    var reg = new RegExp("(^|&)" + param + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) {
      return unescape(r[2]); //返回参数值
    } else {
      return null;
    }
}