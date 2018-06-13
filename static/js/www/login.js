if (! ("placeholder" in document.createElement("input"))) {
    Core.noSupportPlaceholder = true;
    $("#useremail_box label").css("display", "");
    $("#password_box label").css("display", "")
}

$("#AutoLogin").click(function() {
    var e = $("[name=savelogin]");
    if ($(this).attr("class").indexOf("m-checked") != -1) {
        $(this).removeClass("m-checked");
        e.val(0)
    } else {
        $(this).addClass("m-checked");
        e.val(1)
    }
});

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