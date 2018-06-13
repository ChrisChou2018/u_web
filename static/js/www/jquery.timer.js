getTime = function (milliseconds) {
    var m_seconds = milliseconds % 1e3,
    time_array = new Array("00", "00", "00");  // 时 分 秒
    if (milliseconds < 100) { // 不足一秒
        return time_array;
    }
    milliseconds -= m_seconds;  // 整数毫秒
    milliseconds /= 1e3;　　// 总秒
    var t = milliseconds % 60;  // 秒
    time_array[2] = "0" + t;  //
    time_array[2] = time_array[2].substr(time_array[2].length - 2);
    milliseconds -= t; // 时分的和=秒
    milliseconds /= 60;　// 时分的和=分
    t = milliseconds % 60;　// 分
    time_array[1] = "0" + t;　// 分
    time_array[1] = time_array[1].substr(time_array[1].length - 2);
    milliseconds -= t,  // 时=分
    milliseconds /= 60;  // 时
    t = milliseconds;
    time_array[0] = "0" + t;
    time_array[0] = time_array[0].substr(time_array[0].length - 2);

    return time_array
}

var timer = null;
temai_timer = function() {
    var el_timer_l = $(".timerBox1-home"),
    now = (new Date).getTime();
    if (el_timer_l.length === 1) {
        timer = setInterval(function() {
            var arr = getTime(parseFloat(el_timer_l.attr("timer")) - ((new Date).getTime() - now));
            $(".timerBox1-home strong.hour").text(arr[0]); //时
            $(".timerBox1-home strong.min").text(arr[1]);　//分
            $(".timerBox1-home strong.sec").text(arr[2]);　//秒
        },
        100)
    }
}

temai_timer_stop = function() {
    if(timer){
        clearInterval(timer);
    }
};