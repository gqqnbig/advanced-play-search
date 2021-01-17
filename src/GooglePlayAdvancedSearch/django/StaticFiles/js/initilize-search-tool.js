const currentQuery = new URLSearchParams(location.search);
//Cannot write map(parseInt) because parseInt can accept 2 parameters!
const excludedPIds = currentQuery.has('pids') ? currentQuery.get('pids').split(',').map(n => parseInt(n)) : [];
const excludedCIds = currentQuery.has('cids') ? currentQuery.get('cids').split(',').map(n => parseInt(n)) : [];

const searchTool = new Vue({
	el: '#searchTool',
	data: {
		keyword: currentQuery.get('q') || '',
		isSearchButtonEnabled: false,
		permissionFilter: {
			items: [],
		},
		categoryFilter: {
			items: [],
		},
		sortType: currentQuery.get('sort') || '', // if currentQuery.get('sort')  is falsy, return empty string.
		allowInAppPurchase: !currentQuery.get('ap'),
		freeInstall: currentQuery.get('free') || false,
		allowAds: !currentQuery.get('ad'),
	},
	computed: {
		queryString: function () {
			let query = `q=${encodeURIComponent(this.keyword)}`;
			let excludedPIds = this.permissionFilter.items.filter(p => !p.checked).map(p => p.id).join(',');
			if (excludedPIds)
				query += "&pids=" + excludedPIds;
			let excludedCIds = this.categoryFilter.items.filter(p => !p.checked).map(p => p.id).join(',');
			if (excludedCIds)
				query += "&cids=" + excludedCIds;
			if (this.sortType)
				query += "&sort=" + this.sortType;
			if (!this.allowInAppPurchase)
				query += "&ap=false";
			if (!this.allowAds)
				query += "&ad=false";
			if (this.freeInstall)
				query += "&free=true";
			return query;
		}
	},
	watch: {
		freeInstall: function (val, oldVal) {
			if (val && this.sortType.startsWith('f'))
				this.sortType = ''; //free to install then price is all 0, nothing to sort.
		},
		sortType: function (val, oldVal) {
			if (val.startsWith('f') && this.freeInstall)
				this.freeInstall = false; //If you want to sort prices, do not tick free to install.
		}
	}
});

const permissionPromise = fetch('/Api/Permissions').then(r => r.json()).then(data => {
	res = Object.entries(data).map(p => {
		return {id: parseInt(p[0]), name: p[1], checked: !excludedPIds.includes(parseInt(p[0]))}
	});
	res.sort((x, y) => x.name.localeCompare(y.name));
	searchTool.permissionFilter.items = res
});

const categoryPromise = fetch('/Api/Categories').then(r => r.json()).then(data => {
	res = Object.entries(data).map(p => {
		return {id: parseInt(p[0]), name: p[1], checked: !excludedCIds.includes(parseInt(p[0]))}
	});
	res.sort((x, y) => x.name.localeCompare(y.name));
	searchTool.categoryFilter.items = res;
});