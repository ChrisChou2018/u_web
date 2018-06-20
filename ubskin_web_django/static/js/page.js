//分页插件
/**
 * 根据　http://www.lanrenzhijia.com/ajaxjs/jquery.page.js　改写
**/
(function($){
	var ms = {
		init:function(obj,args){
			return (function(){
				ms.fillHtml(obj,args);
				ms.bindEvent(obj,args);
			})();
		},
		//填充html
		fillHtml:function(obj,args){
			return (function(){
				obj.empty();
				//上一页
				if(args.current > 1){
					obj.append('<a href="javascript:;" onclick="" class="prevPage">上一页</a>');
				}else if (args.pageCount > 1){
					obj.remove('.prevPage');
					obj.append('<span class="disabled prevPage">上一页</span>');
				}
				//中间页码
				if(args.current != 1 && args.current >= 4 && args.pageCount != 4){
					obj.append('<a href="javascript:;" class="tcdNumber">'+1+'</a>');
				}
				if(args.current-2 > 2 && args.current <= args.pageCount && args.pageCount > 5){
					obj.append('<span>...</span>');
				}
				var start = args.current -2,end = args.current+2;
				if((start > 1 && args.current < 4)||args.current == 1){
					end++;
				}
				if(args.current > args.pageCount-4 && args.current >= args.pageCount){
					start--;
				}
				for (;start <= end; start++) {
					if(start <= args.pageCount && start >= 1){
						if(start != args.current){
							obj.append('<a href="javascript:;" class="tcdNumber">'+ start +'</a>');
						}else if (args.pageCount > 1){
							obj.append('<span class="current">'+ start +'</span>');
						}
					}
				}
				if(args.current + 2 < args.pageCount - 1 && args.current >= 1 && args.pageCount > 5){
					obj.append('<span>...</span>');
				}
				if(args.current != args.pageCount && args.current < args.pageCount -2  && args.pageCount != 4){
					obj.append('<a href="javascript:;" class="tcdNumber">'+args.pageCount+'</a>');
				}
				//下一页
				if(args.current < args.pageCount){
					obj.append('<a href="javascript:;" class="nextPage">下一页</a>');
				}else if (args.pageCount > 1){
					obj.remove('.nextPage');
					obj.append('<span class="disabled nextPage">下一页</span>');
				}
			})();
		},
		//绑定事件
		bindEvent:function(obj,args){
			return (function(){
				obj.find("a.tcdNumber").click(function(){
					var current = parseInt($(this).text());
					ms.fillHtml(obj,{"current":current,"pageCount":args.pageCount});
					if(typeof(args.backFn)=="function"){
						args.backFn(args.id, current);
					}
				});
				//上一页
				obj.find("a.prevPage").click(function(){
					var current = parseInt(obj.children("span.current").text());
					ms.fillHtml(obj,{"current":current-1,"pageCount":args.pageCount});
					if(typeof(args.backFn)=="function"){
						args.backFn(args.id, current-1);
					}
				});
				//下一页
				obj.find("a.nextPage").click(function(){
					var current = parseInt(obj.children("span.current").text());
					ms.fillHtml(obj,{"current":current+1,"pageCount":args.pageCount});
					if(typeof(args.backFn)=="function"){
						args.backFn(args.id, current+1);
					}
				});
			})();
		}
	};
	$.fn.createPage = function(options){
		var args = $.extend({
			pageCount : 1,
			current : 1,
			backFn : function(){},
            goods_id: ""
		},options);
		ms.init(this,args);
	}
})(jQuery);