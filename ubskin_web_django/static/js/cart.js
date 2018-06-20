(function( $ ) {
    $.Shop = function( element ) {
        this.$element = $( element );
        this.init();
    };

    $.Shop.prototype = {
        init: function() {

            // Properties

		    // 会话存储(Session storage):
		    //    1、写入数据，我们可以使用sessionStorage.setItem( name, value )，
            //       也可以更新内容;
            //    2、使用 sessionStorage.removeItem(name) 方法来销毁某一项;
            //    3、使用 sessionStorage.clear() 来销毁所有的内容;
			this.storage = sessionStorage;

            this.cartPrefix = "mhs-"; // key 的名称的前缀
            this.cartName = this.cartPrefix + "cart"; // 购物车 key 名称
            // this.shippingRates = this.cartPrefix + "shipping-rates"; // Shipping rates key in the session storage
            this.total = this.cartPrefix + "total"; // 总价格 key 名称


            this.$formAddToCart = this.$element.find( "form.add-to-cart" ); // 添加商品的表单
            this.$formCart = this.$element.find( "#shopping-cart" ); // 购物车表单
            this.$checkoutCart = this.$element.find( "#checkout-cart" ); // 结账表单
            this.$checkoutOrderForm = this.$element.find( "#checkout-order-form" ); // 结账表单中的客户填写信息
            this.$shipping = this.$element.find( "#sshipping" ); // 显示运费的元素
            this.$subTotal = this.$element.find( "#stotal" ); // 显示总价的元素
            this.$shoppingCartActions = this.$element.find( "#shopping-cart-actions" ); // 购物车操作相关的元素
            this.$updateCartBtn = this.$shoppingCartActions.find( "#update-cart" ); // 更新购物车的按钮
            this.$emptyCartBtn = this.$shoppingCartActions.find( "#empty-cart" ); // 清空购物车的按钮


            this.currency = "$";
            this.currencyString = "$"; // 当前货币符号，我们使用人民币： $

            // Object containing patterns for form validation
            this.requiredFields = {
                expression: {
                    value: /^([\w-\.]+)@((?:[\w]+\.)+)([a-z]){2,4}$/
                },
                str: {
                    value: ""
                }
            };

            // Method invocation
            this.createCart();
            this.handleAddToCartForm();
            this.handleCheckoutOrderForm();
            this.emptyCart();
            this.updateCart();
            this.displayCart();
            this.deleteProduct();
            this.displayUserDetails();
            this.populatePayPalForm();

        },

        // Public methods

        // Creates the cart keys in the session storage
        createCart: function() {
        },

        // Appends the required hidden values to the PayPal's form before submitting
        populatePayPalForm: function() {
        },

        // Displays the user's information
        displayUserDetails: function() {
        },

        // Delete a product from the shopping cart
        deleteProduct: function() {
        },

        // Displays the shopping cart
        displayCart: function() {
        },

        // Empties the cart by calling the _emptyCart() method
        // @see $.Shop._emptyCart()
        emptyCart: function() {
        },

        // Updates the cart

        updateCart: function() {
        },

        // Adds items to the shopping cart
        handleAddToCartForm: function() {
        },

        // Handles the checkout form by adding a validation routine and saving user's info into the session storage
        handleCheckoutOrderForm: function() {
        },

        // Private methods


        // Empties the session storage
        _emptyCart: function() {
            this.storage.clear();
        },

        /* Format a number by decimal places
         * @param num Number the number to be formatted
         * @param places Number the decimal places
         * @returns n Number the formatted number
         */

        _formatNumber: function( num, places ) {
            var n = num.toFixed( places );
            return n;
        },

        /* Extract the numeric portion from a string
         * @param element Object the jQuery element that contains the relevant string
         * @returns price String the numeric string
         */


        _extractPrice: function( element ) {
            var self = this;
            var text = element.text();
            var price = text.replace( self.currencyString, "" ).replace( " ", "" );
            return price;
        },

        /* Converts a numeric string into a number
         * @param numStr String the numeric string to be converted
         * @returns num Number the number
         */

        _convertString: function( numStr ) {
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

        /* Converts a number to a string
         * @param n Number the number to be converted
         * @returns str String the string returned
         */

        _convertNumber: function( n ) {
            var str = n.toString();
            return str;
        },

        /* Converts a JSON string to a JavaScript object
         * @param str String the JSON string
         * @returns obj Object the JavaScript object
         */

        _toJSONObject: function( str ) {
            var obj = JSON.parse( str );
            return obj;
        },

        /* Converts a JavaScript object to a JSON string
         * @param obj Object the JavaScript object
         * @returns str String the JSON string
         */

        _toJSONString: function( obj ) {
            var str = JSON.stringify( obj );
            return str;
        },


        /* Add an object to the cart as a JSON string
         * @param values Object the object to be added to the cart
         * @returns void
         */

        _addToCart: function( values ) {
            var cart = this.storage.getItem( this.cartName );

            var cartObject = this._toJSONObject( cart );
            var cartCopy = cartObject;
            var items = cartCopy.items;
            items.push( values );

            this.storage.setItem( this.cartName, this._toJSONString( cartCopy ) );
        },

        /* Custom shipping rates calculation based on the total quantity of items in the cart
         * @param qty Number the total quantity of items
         * @returns shipping Number the shipping rates
         */

        _calculateShipping: function( qty ) {
            var shipping = 0;
            if( qty >= 6 ) {
                shipping = 10;
            }
            if( qty >= 12 && qty <= 30 ) {
                shipping = 20;
            }

            if( qty >= 30 && qty <= 60 ) {
                shipping = 30;
            }

            if( qty > 60 ) {
                shipping = 0;
            }

            return shipping;

        },

        /* Validates the checkout form
         * @param form Object the jQuery element of the checkout form
         * @returns valid Boolean true for success, false for failure
         */

        _validateForm: function( form ) {
            var self = this;
            var fields = self.requiredFields;
            var $visibleSet = form.find( "fieldset:visible" );
            var valid = true;

            form.find( ".message" ).remove();

          $visibleSet.each(function() {

            $( this ).find( ":input" ).each(function() {
                var $input = $( this );
                var type = $input.data( "type" );
                var msg = $input.data( "message" );

                if( type == "string" ) {
                    if( $input.val() == fields.str.value ) {
                        $( "<span class='message'/>" ).text( msg ).
                        insertBefore( $input );

                        valid = false;
                    }
                } else {
                    if( !fields.expression.value.test( $input.val() ) ) {
                        $( "<span class='message'/>" ).text( msg ).
                        insertBefore( $input );

                        valid = false;
                    }
                }

            });
          });

            return valid;

        },

        /* Save the data entered by the user in the ckeckout form
         * @param form Object the jQuery element of the checkout form
         * @returns void
         */

        _saveFormData: function( form ) {
            var self = this;
            var $visibleSet = form.find( "fieldset:visible" );

            $visibleSet.each(function() {
                var $set = $( this );
                if( $set.is( "#fieldset-billing" ) ) {
                    var name = $( "#name", $set ).val();
                    var email = $( "#email", $set ).val();
                    var city = $( "#city", $set ).val();
                    var address = $( "#address", $set ).val();
                    var zip = $( "#zip", $set ).val();
                    var country = $( "#country", $set ).val();

                    self.storage.setItem( "billing-name", name );
                    self.storage.setItem( "billing-email", email );
                    self.storage.setItem( "billing-city", city );
                    self.storage.setItem( "billing-address", address );
                    self.storage.setItem( "billing-zip", zip );
                    self.storage.setItem( "billing-country", country );
                } else {
                    var sName = $( "#sname", $set ).val();
                    var sEmail = $( "#semail", $set ).val();
                    var sCity = $( "#scity", $set ).val();
                    var sAddress = $( "#saddress", $set ).val();
                    var sZip = $( "#szip", $set ).val();
                    var sCountry = $( "#scountry", $set ).val();

                    self.storage.setItem( "shipping-name", sName );
                    self.storage.setItem( "shipping-email", sEmail );
                    self.storage.setItem( "shipping-city", sCity );
                    self.storage.setItem( "shipping-address", sAddress );
                    self.storage.setItem( "shipping-zip", sZip );
                    self.storage.setItem( "shipping-country", sCountry );

                }
            });
        }
    };

    $(function() {
        var shop = new $.Shop( "#site" );
    });

})( jQuery );
