import { pageUrl, apiUrl } from "../url.js"


class UserPage {
    constructor() {
        this.logoutButton = document.getElementById("user-logout-tab")
        this.elementInfoUser = document.querySelector(".info-user")
    }

    async init() {
        this.addLogoutEvent()
    }

    addLogoutEvent() {
        this.logoutButton.addEventListener("click", async () => {
            console.log("logout")
            await fetch(apiUrl.logoutUser, {"method":"POST"})
            window.location.href = pageUrl.mainPage
        })
    }
}

export { UserPage }