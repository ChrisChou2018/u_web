var selectList = ["s_year", "s_month", "s_day"]; // 三个select的 name

var MONTHS = [1,2,3,4,5,6,7,8,9,10,11,12],
    DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
    YEAR_RANGE = 50;  // 最近 50 年

var selectedYear;

function getYears(range) {
    // range 决定距离现在最近多少年
    var current_year = new Date().getFullYear();
    var year_list =  Array.apply(null, Array(range)).map(function(_, i){return current_year-i;});
    return year_list.reverse();
}

function getMonths() {
    // 月份
    var el_year = document.getElementById(selectList[0]);
    var year = el_year.value;
    if (parseInt(year) === 0) {
        return []
    }
    return MONTHS;
}

function getDays() {
    // 根据年份和月份获取天数
    var days = DAYS;
    var ds;
    // 判断是否为闰年
    var el_month = document.getElementById(selectList[1]);
    var month = el_month.value;
    if (parseInt(month) === 2) {
        var el_year = document.getElementById(selectList[0]);
        var year = el_year.value;
        if ((year%100 == 0 && year%4 == 0) ||
            (year%100 != 0 && year%4 == 0)) {
            // 闰年
            ds = Array.apply(null, Array(29)).map(function(_, i){return i+1;})
        } else {
            ds = Array.apply(null, Array(28)).map(function(_, i){return i+1;})
        }
    } else if (parseInt(month) === 0) {
        ds = []
    }else {
        ds = Array.apply(null, Array(days[parseInt(month)-1])).map(function(_, i){return i+1;});
    }
    return ds;
}

function initTimeSelect() {
    var year_list = getYears(YEAR_RANGE);
}

function getCurrentData(index) {
    // 根据坐标选择现在需要的相应的数据
    if (index === 0) {return getYears(YEAR_RANGE);}
    if (index === 1) {return getMonths();}
    if (index === 2) {return getDays();}
}

function changeTime(select){
    var el = document.getElementById(selectList[select]);
    with(el) {
        options.length=0;
        options[0] = new Option("请选择", 0);
        var data = getCurrentData(select);
        for (var i = 0; i < data.length; i++) {
            options[i+1] = new Option(data[i], data[i]);
        }
        options[0].selected = true;
        if(++select < selectList.length) {
            changeTime(select);
        }
    }
}

function _init_time(){  // 初始化函数
    for(var i=0; i < selectList.length-1; i++){
        document.getElementById(selectList[i]).onchange = new Function("changeTime("+(i+1)+")");
    }
    for(var i=0; i < selectList.length; i++){
        var el = document.getElementById(selectList[i]);
        el.options[0] = new Option("请选择", 0);
    }
    changeTime(0);
}