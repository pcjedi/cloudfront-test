// Live clock
function updateClock() {
	const el = document.getElementById("clock");
	if (el) {
		el.textContent = new Date().toLocaleTimeString();
	}
}
updateClock();
setInterval(updateClock, 1000);

// Page load time
window.addEventListener("load", () => {
	const el = document.getElementById("load-time");
	if (el && performance.timing) {
		const ms =
			performance.timing.domContentLoadedEventEnd -
			performance.timing.navigationStart;
		el.textContent = ms + " ms";
	}
});

// Viewer region from CloudFront headers (falls back to timezone)
(() => {
	const el = document.getElementById("region");
	if (el) {
		const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
		el.textContent = tz || "Unknown";
	}
})();
