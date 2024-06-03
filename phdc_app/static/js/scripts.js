const body = document.querySelector("body"),
      homea_navbar = document.querySelector(".homea-navbar"),
	  homea_nav_menu = document.querySelector(".homea-nav-menu"),
	  search_toggle = document.querySelector(".homea-nav-search-toggle"),
	  sidebar_menu = document.querySelector(".sidebar-menu");

	  search_toggle.addEventListener("click", () => {
		search_toggle.classList.toggle("active");
	  });

	  sidebar_menu.addEventListener("click", () => {
		homea_navbar.classList.add("active");
	  });

    body.addEventListener("click", item => {
		let activeItem = item.target;

		if(!activeItem.classList.contains("sidebar-menu") && !activeItem.classList.contains("homea-nav-menu")) {
			homea_navbar.classList.remove("active");
		}
    });

document.addEventListener("DOMContentLoaded", function(event) { 
	const modal = new bootstrap.Modal(document.getElementById("modal"))

	htmx.on("htmx:afterSwap", (e) => {
		if (e.detail.target.id == "dialog") {
		  modal.show()
		}
	})

	htmx.on("htmx:beforeSwap", (e) => {
		if (e.detail.target.id == "dialog" && !e.detail.xhr.response) {
		  modal.hide()
		  e.detail.shouldSwap = false
		}
	})

	htmx.on("hidden.bs.modal", () => {
		document.getElementById("dialog").innerHTML = ""
	  })
});










