    async function cleanupOldCaches(){try{if(!('caches'in window))return;const keys=await caches.keys();await Promise.all(keys.filter(k=>k.startsWith('chaselights-')&&k!==CACHE_NAME).map(k=>caches.delete(k)));}catch{}}
    function initializeApp(){cleanupOldCaches();applyStaticI18n();renderSubNav();syncDayButtons();loadData(currentRegion);}
    initializeApp();
