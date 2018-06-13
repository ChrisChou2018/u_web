(function( $ ) {

    $.Cart = function( ) {
        // Properties
        this.isLogin     = false;
		this.items       = new Array()
        this.totalCount  = 0;  // 总数量
    };

    $.Item = function() {
        // Properties
        this.GoodsId = "";
        this.Count   = 0;
    }

    $.CartHelper = function() {
        // Properties
        this.cartName = "mhs-cart"; // 购物车名称
        this.cartNumElement = ".shopcart > .num, #newcartnum";  // 也购物车元素

        // 初始化
        this.init();
    }

    $.CartHelper.prototype = {

        //
        // 共有方法
        //

        // 创建一个购物车, 可能之前有购物车
        // 并初始化界面元素
        init: function() {
            var self = this;
            var source = $.cookie(self.cartName);
            if ( source == null || source == "" ) {
                var ca = new $.Cart();
                self.saveCart(ca)
            }

            var cart = self._getCart();
            // 初始化页面中的相关元素
            self.initCartHtml();
            var login = new $.LoginMhs( );
            // 仅仅刚刚登录并且之前没有合并的时候采取做合并操作
            if ( login.isLogin() && cart.isLogin == false ) {
                // TODO: 合并购物车

                // step1: 发送本地 cookie 中的购物车到后台数据库

                // step2: 获取后台数据库购物车和本地 cookie 合并

                cart.isLogin = true;
            }
            self.saveCart(cart);  // 保存购物车
        },

        /*
        ** 初始化页面中的相关元素
        */
        initCartHtml: function() {
            var self = this;
            var cart = self._getCart();
            try {
                // 兼容移动版本
                $(self.cartNumElement).text(cart.totalCount);
            } catch (e){}
        },

        // 删除一个购物车内容
        deleteProduct: function(goodsId) {
			var self = this;
            var cart = self._getCart();
            // 用于判断是更新还是重新添加，没有找到则是表示重新添加
            var index = self._findItem(goodsId, cart);
            try {
                cart.totalCount -= cart.items[index].Count;
            } catch (e) {
            } finally {
                // var deleteIndex = cart.items.indexOf(cart.items[index]);
                cart.items.splice(index, 1); // 删除指定位置的元素
                self.saveCart(cart);
            }
        },

        // 保存购物车操作
        saveCart: function(cart) {
            var self = this;

            // 将 cart.items 转换为 json 字符串对象
            var source = {"totalCount": cart.totalCount,
                          "items": cart.items,
                          "isLogin": cart.isLogin}
            var cartString = self._toJSONString(source)
            var cookie = $.cookie(self.cartName, cartString, {expires: 24*3600, path: '/'})
            // cookie.setPath("/");
        },

        // 清空购物车
        emptyCart: function() {
            var self = this
            var cart = new $.Cart();
            self.saveCart(cart)
        },

        // 更新购物车
        updateCart: function(goodsId, count) {
			var self = this;
            count = self._convertStringToNum(count);
            if (goodsId) {
                self._updateItem(goodsId, count);
            }
        },

        // 获取购物车对象
        getCart: function() {
            var self = this;
            return self._getCart();
        },

        // 更新线上、未登录前购物车合并到本地
        mergeCart: function(onlineCart, cart) {
            var self = this;
            for (var i = 0; i < onlineCart.length; i++) {
                var index  = self._findItem(onlineCart[i]["goods_id"], cart);
                if (index >= 0) {
                    // 更新该商品数目
                    cart.items[index].Count += onlineCart[i]["goods_count"];
                    // 更新总商品数目
                    cart.totalCount += onlineCart[i]["goods_count"];
                } else {
                    var item = new $.Item();
                    item.GoodsId = onlineCart[i]["goods_id"];
                    item.Count = onlineCart[i]["goods_count"];
                    cart.items.push(item);  // 添加商品到购物车
                    // 更新总商品数
                    cart.totalCount += onlineCart[i]["goods_count"];
                }
            }
            self.saveCart(cart);
        },


        /*
        ** 私有方法
        */

        // 查找购物车中的某一项目，有则返回 index, 没有返回 -1
        _findItem: function(goodsId, cart){
            for (var i = 0; i < cart.items.length; i++) {
                if ( cart.items[i].GoodsId == goodsId) {
                    return i
                }
            }
            return -1;
        },

        _getCart: function() {
            var self = this
            var source = $.cookie(self.cartName);
            var cart = new $.Cart();
            if ( source == null || source == "" ) {
                return cart;
            }

            var cartObj     = self._toJSONObject(source);
            cart.items      = cartObj.items;
            cart.totalCount = cartObj.totalCount;
            cart.isLogin    = cartObj.isLogin;

            return cart;
        },

        /*
        ** 更新购物车，可以是更新商品或者添加新的商品
        ** @param goodsId: 需要更新或者添加的商品ID
        ** @param changeCount: 正数表示添加，负数表示减少
        ** @returns void
        */
        _updateItem: function(goodsId, changeCount) {
            var self = this;
            var cart = this._getCart();
            /*
            ** 更新购物车中的 item 信息
            */
            // 用于判断是更新还是重新添加，没有找到则是表示重新添加
            var updated = false;
            var index = self._findItem(goodsId, cart);
            if (index >= 0) {
                cart.items[index].Count = cart.items[index].Count + changeCount;
                if ( cart.items[index].Count <= 0 ) {  // 商品书小于等于0，则移除商品
                    // var deleteIndex = cart.items.indexOf(cart.items[i]);
                    cart.items.splice(index, 1); // 删除指定位置的元素
                }
            } else if (changeCount > 0) {  // // 只有 changeCount > 0 才需要添加商品
                var item = new $.Item();
                item.GoodsId = goodsId;
                item.Count = changeCount;
                cart.items.push(item);  // 添加商品到购物车
            }

            cart.totalCount = cart.totalCount + changeCount; // 修改总购物车数量
            self.saveCart(cart);  // 保存购物车
        },
        

        _formatNumber: function( num, places ) {
            var n = num.toFixed( places );
            return n;
        },

        _extractPrice: function( element ) {
            var self = this;
            var text = element.text();
            var price = text.replace( self.currencyString, "" ).replace( " ", "" );
            return price;
        },

        /*
        ** 将一个字符串转换为number
        */
        _convertStringToNum: function( numStr ) {
            var num;
            if( /^[-+]?[0-9]+\.[0-9]+$/.test( numStr ) ) {
                num = parseFloat( numStr );
            } else if( /^\d+$/.test( numStr ) ) {
                num = parseInt( numStr, 10 );
            } else {
                num = Number( numStr );
            }

            if( !isNaN( num ) ) {
                return num;
            } else {
                console.warn( numStr + " cannot be converted into a number" );
                return false;
            }
        },

        /*
        ** 将一个 number 转换为字符串
        */
        _convertNumToNum: function( n ) {
            var str = n.toString();
            return str;
        },

        /*
        ** i将一个 JSON 字符串转换为一个 JavaScript 对象
        ** @param： str JSON 字符串
        ** @return： JavaScript object
        */
        _toJSONObject: function( str ) {
            var obj = JSON.parse( str );
            return obj;
        },

        /*
        ** 将一个 javascript 对象转换为一个 JSON 字符串对象
        ** @param:  obj javascript 对象
        ** @return: JSON 字符串对象
        */
        _toJSONString: function( obj ) {
            var str = JSON.stringify( obj );
            return str;
        },


        /*
        ** 将一个 JSON 字符串加入到购物车
         * @param:  values 添加多购物车的对象
         * @returns:    无
         */
        _addToCart: function( values ) {
            var cart = this.storage.getItem( this.cartName );

            var cartObject = this._toJSONObject( cart );
            var cartCopy = cartObject;
            var items = cartCopy.items;
            items.push( values );

            this.storage.setItem( this.cartName, this._toJSONString( cartCopy ) );
        },

        /*
        ** 计算总价
        */
		_calculateTotal: function( qty ) {
			var shipping = 0;

            // TODO： 计算总价

			return shipping;

		},
    };

    // 对象实例在页面初始化(被加载)时被创建
    $(function() {
        new $.CartHelper();
    });

})( jQuery );
