(function( $ ) {

    $.LoginMhs = function() {
        // Properties
        this.loginFlag = "mhsc1"; // 是否登录的 key

    }

    $.LoginMhs.prototype = {

        isLogin: function() {
            var self = this;
            var isLogin = $.cookie(self.loginFlag);
            if ( isLogin == null || isLogin == "" ) {
                return false;
            }
            return true;
        }
    };

})( jQuery );
