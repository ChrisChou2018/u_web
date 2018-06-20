// 移动版本 cookie 使用, 和 web 版本兼容
(function( $ ) {

    $.LoginMhs = function() {
        // Properties
        this.loginFlag = "mhsc1"; // 是否登录的 key
    };

    $.LoginMhs.prototype = {
        isLogin: function() {
            var self = this;
            return $.cookie(self.loginFlag);
        }
    };

})( jQuery );

(function( $ ) {
    $.cookie = function (key, value, options) {
        if (arguments.length > 1 && (null === value || "object" !== typeof value)) {
            //o = $.cookie.extend({}, o);
            options = $.cookie._getExtendedOptions(options);
            if (null === value) options.expires = -1;
            if ("number" === typeof options.expires) {
                var r = options.expires,
                    a = options.expires = new Date;
                a.setDate(a.getDate() + r)
            }
            return window.document.cookie = [encodeURIComponent(key), "=", options.raw ? String(value) : encodeURIComponent(String(value)), options.expires ? "; expires=" + options.expires.toUTCString() : "", options.path ? "; path=" + options.path : "", options.domain ? "; domain=" + options.domain : ""].join("")
        }
        options = value || {};
        var s, c = options.raw ? function (e) {
            return e
        } : decodeURIComponent;
        return (s = new RegExp("(?:^|; )" + encodeURIComponent(key) + "=([^;]*)").exec(window.document.cookie)) ? c(s[1]) : null
    };

    $.cookie.defaults = {
        path: '/',
        // domain: "meihuishuo.com",
        expires: 1
    };

    $.cookie._getExtendedOptions = function (options) {
        return {
            path: options && options.path || $.cookie.defaults.path,
            domain: options && options.domain || $.cookie.defaults.domain,
            expires: options && options.expires || $.cookie.defaults.expires
        };
    };
})( jQuery );