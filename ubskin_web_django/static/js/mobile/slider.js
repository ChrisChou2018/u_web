function Swipe(container, options) {
    "use strict";

    var noop = function() {};
    var offloadFn = function(fn) {  // 停止
        setTimeout(fn || noop, 0)
    };
    // transition动作上保证浏览器的兼容性
    var browser = {
        addEventListener: !!window.addEventListener,
        touch: ('ontouchstart' in window) || window.DocumentTouch && document instanceof DocumentTouch,
        transitions: (function(temp) {
            var props = ['transitionProperty', 'WebkitTransition', 'MozTransition', 'OTransition', 'msTransition'];
            for (var i in props) if (temp.style[props[i]] !== undefined) return true;
            return false;
        })(document.createElement('swipe'))
    };
    // quit if no root element
    if (!container) return;

    var element = container.children[0];
    var slides, slidePos, width, length;
    options = options || {};
    var index = parseInt(options.startSlide, 10) || 0;
    var speed = options.speed || 300;
    options.continuous = options.continuous !== undefined ? options.continuous: true;
    function setup() {
        slides = element.children;  // 轮番图
        length = slides.length;  // 个数
        // 是否连续（一个则不会不连续）
        if (slides.length < 2) options.continuous = false;
        //special case if two slides
        if (browser.transitions && options.continuous && slides.length < 3) {
            element.appendChild(slides[0].cloneNode(true));
            element.appendChild(element.children[1].cloneNode(true));
            slides = element.children;
        }
        // create an array to store current positions of each slide
        slidePos = new Array(slides.length);
        // determine width of each slide
        width = container.getBoundingClientRect().width || container.offsetWidth;
        element.style.width = (slides.length * width) + 'px';
        // stack elements
        var pos = slides.length;
        while (pos--) {
            var slide = slides[pos];
            slide.style.width = width + 'px';
            slide.setAttribute('data-index', pos);
            if (browser.transitions) {
                slide.style.left = (pos * -width) + 'px';
                move(pos, index > pos ? -width: (index < pos ? width: 0), 0);
            }
        }
        // reposition elements before and after index
        if (options.continuous && browser.transitions) {
            move(circle(index - 1), -width, 0);
            move(circle(index + 1), width, 0);
        }
        if (!browser.transitions) element.style.left = (index * -width) + 'px';
        container.style.visibility = 'visible';
    }
    function prev() {
        if (options.continuous) slide(index - 1);
        else if (index) slide(index - 1);
    }
    function next() {
        if (options.continuous) slide(index + 1);
        else if (index < slides.length - 1) slide(index + 1);
    }
    function circle(index) {
        // a simple positive modulo using slides.length
        return (slides.length + (index % slides.length)) % slides.length;
    }
    function slide(to, slideSpeed) {
        // // 如果已经滑动不做任何事情
        if (index == to) return;
        if (browser.transitions) {
            // 滑动方向 1: 向后, -1: 向前
            var direction = Math.abs(index - to) / (index - to);
            // 获取位置
            if (options.continuous) {
                var natural_direction = direction;
                direction = -slidePos[circle(to)] / width;
                if (direction !== natural_direction) to = -direction * slides.length + to;
            }
            var diff = Math.abs(index - to) - 1;
            while (diff--) move(circle((to > index ? to: index) - diff - 1), width * direction, 0);
            to = circle(to);
            move(index, width * direction, slideSpeed || speed);
            move(to, 0, slideSpeed || speed);
            if (options.continuous) move(circle(to - direction), -(width * direction), 0);
        } else {
            to = circle(to);
            animate(index * -width, to * -width, slideSpeed || speed);
        }
        index = to;
        offloadFn(options.callback && options.callback(index, slides[index]));
    }
    // 滑动动作
    function move(index, dist, speed) {
        translate(index, dist, speed);
        slidePos[index] = dist;
    }
    // 滑动动作效果
    function translate(index, dist, speed) {
        var slide = slides[index];
        var style = slide && slide.style;
        if (!style) return;
        style.webkitTransitionDuration = style.MozTransitionDuration = style.msTransitionDuration = style.OTransitionDuration = style.transitionDuration = speed + 'ms';
        style.webkitTransform = 'translate(' + dist + 'px,0)' + 'translateZ(0)';
        style.msTransform = style.MozTransform = style.OTransform = 'translateX(' + dist + 'px)';
    }
    function animate(from, to, speed) {
        if (!speed) {
            element.style.left = to + 'px';
            return;
        }
        var start = +new Date;
        var timer = setInterval(function() {
            var timeElap = +new Date - start;
            if (timeElap > speed) {
                element.style.left = to + 'px';
                if (delay) begin();
                options.transitionEnd && options.transitionEnd.call(event, index, slides[index]);
                clearInterval(timer);
                return;
            }
            element.style.left = (((to - from) * (Math.floor((timeElap / speed) * 100) / 100)) + from) + 'px';
        },
        4);
    }

    // 自动运行相关设置
    var delay = options.auto || 0;
    var interval;
    function begin() {
        // 开始自动运行
        interval = setTimeout(next, delay);
    }
    function stop() {
        // 取消自动运行
        delay = 0;
        clearTimeout(interval);
    }
    // 初始化
    var start = {};
    var delta = {};
    var isScrolling;
    // 初始化相关事件
    // 这三个时间只能绑定
    var events = {
        handleEvent: function(event) {
            switch (event.type) {
            case 'touchstart':
                this.start(event);
                break;
            case 'touchmove':
                this.move(event);
                break;
            case 'touchend':
                offloadFn(this.end(event));
                break;
            case 'webkitTransitionEnd':
            case 'msTransitionEnd':
            case 'oTransitionEnd':
            case 'otransitionend':
            case 'transitionend':
                offloadFn(this.transitionEnd(event));
                break;
            case 'resize':
                offloadFn(setup.call());
                break;
            }
            if (options.stopPropagation) event.stopPropagation();
        },
        start: function(event) {
            var touches = event.touches[0];  // 第一个触摸点
            start = {
                // 获取其实坐标
                x: touches.pageX,
                y: touches.pageY,
                // store time to determine touch duration
                time: +new Date
            };
            // 地一个移动事件
            isScrolling = undefined;

            delta = {};
            // touchmove 和 touchend 是原生js，所以只能通过addEventListener绑定
            element.addEventListener('touchmove', this, false);
            element.addEventListener('touchend', this, false);
        },
        move: function(event) {  // 手指滑动的相关计算
            if (event.touches.length > 1 || event.scale && event.scale !== 1) return;
            if (options.disableScroll) event.preventDefault();
            var touches = event.touches[0];
            // 计算移动的坐标
            delta = {
                x: touches.pageX - start.x,
                y: touches.pageY - start.y
            };

            if (typeof isScrolling == 'undefined') {
                isScrolling = !!(isScrolling || Math.abs(delta.x) < Math.abs(delta.y));
            }
            if (!isScrolling) {
                event.preventDefault();
                stop();
                // 如果是地一个或者最后一个，保证连续
                if (options.continuous) {
                    translate(circle(index - 1), delta.x + slidePos[circle(index - 1)], 0);
                    translate(index, delta.x + slidePos[index], 0);
                    translate(circle(index + 1), delta.x + slidePos[circle(index + 1)], 0);
                } else {
                    delta.x = delta.x / ((!index && delta.x > 0　||　index == slides.length - 1　&& delta.x < 0) ? (Math.abs(delta.x) / width + 1)　: 1);
                    translate(index - 1, delta.x + slidePos[index - 1], 0);
                    translate(index, delta.x + slidePos[index], 0);
                    translate(index + 1, delta.x + slidePos[index + 1], 0);
                }
            }
        },
        end: function(event) {  // 停止滑动
            // 计算持续时间
            var duration = +new Date - start.time;
            // 滑动切换向前还是向后
            var isValidSlide = Number(duration) < 250　&&　 Math.abs(delta.x) > 20　||　Math.abs(delta.x) > width / 2;
            // determine if slide attempt is past start and end
            var isPastBounds = !index && delta.x > 0 // if first slide and slide amt is greater than 0
            || index == slides.length - 1 && delta.x < 0; // or if last slide and slide amt is less than 0
            if (options.continuous) isPastBounds = false;
            // determine direction of swipe (true:right, false:left)
            var direction = delta.x < 0;
            // if not scrolling vertically
            if (!isScrolling) {
                if (isValidSlide && !isPastBounds) {
                    if (direction) {
                        if (options.continuous) { // we need to get the next in this direction in place
                            move(circle(index - 1), -width, 0);
                            move(circle(index + 2), width, 0);
                        } else {
                            move(index - 1, -width, 0);
                        }
                        move(index, slidePos[index] - width, speed);
                        move(circle(index + 1), slidePos[circle(index + 1)] - width, speed);
                        index = circle(index + 1);
                    } else {
                        if (options.continuous) { // we need to get the next in this direction in place
                            move(circle(index + 1), width, 0);
                            move(circle(index - 2), -width, 0);
                        } else {
                            move(index + 1, width, 0);
                        }
                        move(index, slidePos[index] + width, speed);
                        move(circle(index - 1), slidePos[circle(index - 1)] + width, speed);
                        index = circle(index - 1);
                    }
                    options.callback && options.callback(index, slides[index]);
                } else {
                    if (options.continuous) {
                        move(circle(index - 1), -width, speed);
                        move(index, 0, speed);
                        move(circle(index + 1), width, speed);
                    } else {
                        move(index - 1, -width, speed);
                        move(index, 0, speed);
                        move(index + 1, width, speed);
                    }
                }
            }
            // kill touchmove and touchend event listeners until touchstart called again
            element.removeEventListener('touchmove', events, false)
            element.removeEventListener('touchend', events, false)
        },
        transitionEnd: function(event) {
            if (parseInt(event.target.getAttribute('data-index'), 10) == index) {
                if (delay) begin();
                options.transitionEnd && options.transitionEnd.call(event, index, slides[index]);
            }
        }
    };
    // trigger setup
    setup();
    // start auto slideshow if applicable
    if (delay) begin();
    // add event listeners
    if (browser.addEventListener) {
        // set touchstart event on element
        if (browser.touch) element.addEventListener('touchstart', events, false);
        if (browser.transitions) {
            element.addEventListener('webkitTransitionEnd', events, false);
            element.addEventListener('msTransitionEnd', events, false);
            element.addEventListener('oTransitionEnd', events, false);
            element.addEventListener('otransitionend', events, false);
            element.addEventListener('transitionend', events, false);
        }
        window.addEventListener('resize', events, false);
    } else {
        window.onresize = function() {
            setup()
        };
    }

    return {
        setup: function() {
            setup();
        },
        slide: function(to, speed) {
            stop();
            slide(to, speed);
        },
        prev: function() {
            stop();
            prev();
        },
        next: function() {
            stop();
            next();
        },
        getPos: function() {
            // 返回当前图片坐标
            return index;
        },
        getNumSlides: function() {
            // 获取图片个数
            return length;
        },
        kill: function() {  // 取消相关操作，并且初始化相关信息
            stop();
            element.style.width = 'auto';
            element.style.left = 0;
            // reset slides
            var pos = slides.length;
            while (pos--) {
                var slide = slides[pos];
                slide.style.width = '100%';
                slide.style.left = 0;
                if (browser.transitions) translate(pos, 0, 0);
            }
            // 删除事件侦听器
            if (browser.addEventListener) {
                element.removeEventListener('touchstart', events, false);
                element.removeEventListener('webkitTransitionEnd', events, false);
                element.removeEventListener('msTransitionEnd', events, false);
                element.removeEventListener('oTransitionEnd', events, false);
                element.removeEventListener('otransitionend', events, false);
                element.removeEventListener('transitionend', events, false);
                window.removeEventListener('resize', events, false);
            } else {
                window.onresize = null;
            }
        }
    }
}
if (window.jQuery || window.Zepto) { (function($) {
        $.fn.Swipe = function(params) {
            return this.each(function() {
                $(this).data('Swipe', new Swipe($(this)[0], params));
            });
        }
    })(window.jQuery || window.Zepto)
}