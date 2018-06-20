var s = ["s_province","s_city","s_county"];//三个select的name

function Dsy(){}

function change(v){

    $.ajaxSettings.async = false;
    if (typeof(dsy.Items) == "undefined") {
        $.getJSON("/js/distpicker/area.json", function (data) {
            dsy.Items = data["root"]
        });
    }
    $.ajaxSettings.async = true;
    var ss = document.getElementById(s[v]);
    if ( v === 0 ){
	    with(ss) {
		    length = 0;
            options[0] = new Option(opt0[v], opt0[v]);
            var province = dsy.Items["province"];
            for (var i = 0; i < province.length; i++) {
                options[i+1] = new Option(province[i]["name"], province[i]["name"]);
            }
            options[0].selected = true;
		    if(++v<s.length){change(v);}
        }
    } else if (v == 1) {
	    with(ss) {
		    length = 0;
            options[0] = new Option(opt0[v], opt0[v]);
            var index = document.getElementById(s[v-1]).selectedIndex;
            var va = document.getElementById(s[v-1]).options[index].text;
            if (index > 0) {
                var province = dsy.Items["province"],
                    city = new Array();
                for (var i = 0; i < province.length; i++) {
                    if (province[i]["name"] == va) {
                        city = province[i]["city"];
                        break;
                    }
                }
                for (var i = 0; i < city.length; i++) {
                    options[i + 1] = new Option(city[i]["name"], city[i]["name"]);
                }
            }
            options[0].selected = true;
		    if(++v<s.length){change(v);}
        }
    } else if (v == 2) {
	    with(ss) {
		    length = 0;
            var index1 = document.getElementById(s[v-2]).selectedIndex;
            var va1 = document.getElementById(s[v-2]).options[index1].text;
            var index2 = document.getElementById(s[v-1]).selectedIndex;
            var va2 = document.getElementById(s[v-1]).options[index2].text;
            options[0] = new Option(opt0[v], opt0[v]);
            if (index2 > 0) {
                var province = dsy.Items["province"];
                var city = new Array();
                var district = new Array();
                for (var i = 0; i < province.length; i++) {
                    if (province[i]["name"] == va1) {
                        city = province[i]["city"];
                        for (var i = 0; i < city.length; i++) {
                            if (city[i]["name"] == va2) {
                                district = city[i]["district"];
                                break;
                            }
                        }
                        break;
                    }
                }
                for (var i = 0; i < district.length; i++) {
                    options[i + 1] = new Option(district[i]["name"], district[i]["name"]);
                }
            }
            options[0].selected = true;
		    if(++v<s.length){change(v);}
        }
    }
}

var opt0 = ["省份","地级市","市、县级市"];//初始值
var dsy = new Dsy();
function _init_area(){  //初始化函数
	for(i=0;i<s.length-1;i++){
	  document.getElementById(s[i]).onchange=new Function("change("+(i+1)+")");
	}
	change(0);
}