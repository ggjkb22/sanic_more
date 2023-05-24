/**
 * @author zhanghuihua@msn.com
 */
(function($){
	$.fn.navMenu = function(){
		return this.each(function(){
			var $box = $(this);
			$box.find("li>a").click(function(){
				var $a = $(this);
				$.get($a.attr("href"), function(html){
					if (html.statusCode == 300 || html.statusCode == 301){
						alertMsg.error(html.message || "出现错误了,但研发人员并未给出明确提示")
					};
					$("#sidebar").find(".accordion").remove().end().append(html).initUI();
					$box.find("li").removeClass("selected");
					$a.parent().addClass("selected");
					navTab.closeAllTab();
				});
				// $.post($a.attr("href"), {}, function(html){
				// 	$("#sidebar").find(".accordion").remove().end().append(html).initUI();
				// 	$box.find("li").removeClass("selected");
				// 	$a.parent().addClass("selected");
				// 	navTab.closeAllTab();
				// });
				return false;
			});
		});
	}
	
	$.fn.switchEnv = function(){
		var op = {cities$:">ul>li", boxTitle$:">a>span"};
		return this.each(function(){
			var $this = $(this);
			$this.click(function(){
				if ($this.hasClass("selected")){
					_hide($this);
				} else {
					_show($this);
				}
				return false;
			});
			
			$this.find(op.cities$).click(function(){
				var $li = $(this);
				$.get($li.find(">a").attr("href"), function(html){
					if (html[DWZ.keys.statusCode] == DWZ.statusCode.timeout){
						alertMsg.error(html.message || "出现错误了,但研发人员并未给出明确提示")
					};
					_hide($this);
					$this.find(op.boxTitle$).html($li.find(">a").html());
					navTab.closeAllTab();
					$("#sidebar").find(".accordion").remove().end().append(html).initUI();
				});
				// $.post($li.find(">a").attr("href"), {}, function(html){
				// 	_hide($this);
				// 	$this.find(op.boxTitle$).html($li.find(">a").html());
				// 	navTab.closeAllTab();
				// 	$("#sidebar").find(".accordion").remove().end().append(html).initUI();
				// });
				return false;
			});
		});
	}
	
	function _show($box){
		$box.addClass("selected");
		$(document).bind("click",{box:$box}, _handler);
	}
	function _hide($box){
		$box.removeClass("selected");
		$(document).unbind("click", _handler);
	}
	
	function _handler(event){
		_hide(event.data.box);
	}
})(jQuery);


