import { clearError } from "../error.js"
import { apiUrl } from "../url.js"
import { setElementHidden } from "../utils.js"
import { AuthService } from "../service/auth.js"

class AuthPage {

    constructor() {
        this.elemenRegisterError = document.getElementById("register-error")
        this.elementLoginError = document.getElementById("login-error")
        this.registerForm = document.getElementById("register-form")
        this.loginForm = document.getElementById("login-form")
        this.buttonRegister = document.getElementById("register-tab")
        this.buttonLogin = document.getElementById("login-tab")
        this.authService = new AuthService(
            this.loginForm,
            this.elementLoginError,
            this.registerForm,
            this.elemenRegisterError
            )
    }
    init() {
        this.bindEvents()
    }

    bindEvents() {
        this.addButtonEvents()
        this.addRegisterFormEvents()
        this.addAuthenticateFormEvents()
    }

    addButtonEvents() {
        console.log(this.buttonRegister)
        this.buttonRegister.addEventListener("click", () => {

            this.loginForm.reset()
            clearError(this.elementLoginError)
            clearError(this.elemenRegisterError)
            setElementHidden(this.registerForm, false)
            setElementHidden(this.loginForm, true)
        })


        this.buttonLogin.addEventListener("click", () => {
            this.registerForm.reset()
            clearError(this.elementLoginError)
            clearError(this.elemenRegisterError)
            setElementHidden(this.registerForm, true)
            setElementHidden(this.loginForm, false)
        })


    }

    addAuthenticateFormEvents() {
        this.loginForm.addEventListener("submit", async (event) => {
            event.preventDefault()

            clearError(this.elementLoginError)
            const formData = new FormData(this.loginForm)
            try {
                await this.authService.authenticateUser(
                    apiUrl.authenticateUser,
                    formData,
                )

            } catch (error) {
                console.log(error)
            }
        })
    }

    addRegisterFormEvents() {
        this.registerForm.addEventListener("submit", async (event) => {
            event.preventDefault()

            clearError(this.elemenRegisterError)

            const formData = new FormData(this.registerForm)
            const objectRegister = {
                username: formData.get("username"),
                password: formData.get("password")
            }
            try {
                await this.authService.registerUser(
                    apiUrl.registerUser,
                    JSON.stringify(objectRegister)
                )

            } catch (error) {
                console.log(error)
            }
        })
    }


}

export { AuthPage }