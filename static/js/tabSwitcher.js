function changeTab(tab) {
  const createTab = document.getElementById("create");
  const joinTab = document.getElementById("join");

  if (tab === "create") {
    createTab.classList.add("active");
    joinTab.classList.remove("active");
    document.querySelector(".tab.active").classList.remove("active");
    document.querySelector(".tab:nth-child(1)").classList.add("active");
  } else {
    createTab.classList.remove("active");
    joinTab.classList.add("active");
    document.querySelector(".tab.active").classList.remove("active");
    document.querySelector(".tab:nth-child(2)").classList.add("active");
  }
}
