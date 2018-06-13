$("#loginin").click(function() {
    var username = $("#username"),
        password = $("#password"),
        error    = $("#LoginErrInfo"),
        useremail_box = $("#useremail_box"),
        password_box = $("#password_box");

    useremail_box.css("borderColor", "#DDD");
    password_box.css("borderColor", "#DDD");
    if (!username.val() && !password.val()) {
        error.text("请输入用户名和密码").parent().css("display", "block");
        useremail_box.css("borderColor", "#D22147");
        password_box.css("borderColor", "#D22147");
        username.focus();
        return false
    }
    if (!username.val()) {
        error.text("请输入用户名").parent().css("display", "block");
        useremail_box.css("borderColor", "#D22147");
        username.focus();
        return false
    }
    if (!password.val()) {
        error.text("请输入密码").parent().css("display", "block");
        password_box.css("borderColor", "#D22147");
        password.focus();
        return false
    }
    error.parent().css("display", "none")
});

$(".ks-dialog-close").click(function() {
    $(".form-step1-1").css("display", "none");
});

function registe_step1() {
    var tel = $("#telephone").val(); //获取手机号
    var telReg = tel.match(/^(0|86|17951)?(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$/);
    $("#telephone-error").css("color", "#D22147");

    //如果手机号码不能通过验证
    if(!telReg){
        $("#telephone-error").text("请输入正确的电话号码").css("display", "block");
        return "error"
    } else {
        $("#telephone-error").text("").css("display", "none");

        jQuery.ajax({
            type: "POST",
            async: true,
            url: "/registe/step1",
            data: {"telephone": tel},
            success: function(data) {
                if (data["status"] == "success") {
                    $("#send-code-succ").css("display", "block");
                    // $(".form-step1-1").attr("class", $(".form-step1-1").className + " active");
                } else if (data["result"] == "error") {
                    $("#telephone-error").text(data["message"]).css("display", "block");
                    return "error"
                }
            },
            error: function() {
                $("#telephone-error").text("服务器繁忙 请稍后再试").css("display", "block");
                return "error"
            },
            dataType: "json"
        });
    }
};


$("#send_code").click(function() {
    // $("#send_code").css("display", "none");
    // $("#resend_code").css("display", "block");
    status = registe_step1();
    if (status != "error") {
        var seconds = 0;
        $('#send_code').text("重发验证码(120s)");
        setInterval(function(){
            seconds += 1;
            $('#send_code').text("重发验证码("+ (120-seconds).toString() + "s)");
            $('#send_code').attr("disabled", "true");
            if(seconds == 120){
                $('#send_code').attr("disabled","false");
                window.clearInterval(int);
            }
        },1000);
    }
});

$("#btn-registe-step2").click(function() {
    var telephone  = $("#telephone").val();
    var code       = $("#code").val();
    var password   = $("#Password").val();
    var repassword = $("#rePassword").val();

    jQuery.ajax({
        type: "POST",
        async: true,
        url: "/registe/step2",
        data: {"telephone": telephone, "password": password, "code": code},
        success: function(data) {
            if (data["status"] == "success") {
            } else if (data["status"] == "error") {
                alert(data["message"]);
                return "error"
            }
        },
        error: function() {
            return "error"
        },
        dataType: "json"
    });
});