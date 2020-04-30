(() => {
	const isMobile = window.matchMedia('(hover:none)').matches;


	Vue.directive('mobile-title', {
		bind: function (el, binding, vnode) {
			if(isMobile)
				el.setAttribute("tabindex",0);
			el.setAttribute('title',binding.value);
		},
		update: function (el, binding, vnode) {
			el.setAttribute('title',binding.value);
		}
	});
})();