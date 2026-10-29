/**
 * @typedef {import('../type.js').ErrorResponse } ErrorResponse
 */
import { showError, errorCode, renderTemplateByErrors } from "../error.js"
import { setElementHidden } from "../utils.js"
import { pageUrl } from "../url.js"

class AuthService {
    constructor(loginForm, elementLoginError, registerForm, elemenRegisterError) {
        this.loginForm = loginForm
        this.elementLoginError = elementLoginError
        this.registerForm = registerForm
        this.elemenRegisterError = elemenRegisterError
        this.pageContainerElement = document.getElementById("page-content")
        this.template_forbidden = document.getElementById("forbidden-template");
        this.template_internal_server = document.getElementById("internal-server-template");
    }

    /**
     * @param {string} url 
     * @param {object} formData 
     */
    async authenticateUser(
        url,
        formData,
    ) {
        const response = await fetch(
            url,
            {
                method: "POST",
                body: formData,
            })
        if (response.ok) {
            this.loginForm.reset()
            window.location.href = pageUrl.userPage
        } else {
            /** @type {ErrorResponse} */
            const error = await response.json()
            if ( !renderTemplateByErrors(error.code, this.pageContainerElement )) {
                showError(this.elementLoginError, error)
            }
        }

    }

    /**
     * @param {string} url 
     * @param {string} jsonStringify 
     */
    async registerUser(
        url,
        jsonStringify,
    ) {
        const response = await fetch(url, {
            method: "POST",
            body: jsonStringify,
            headers: {
                "Content-Type": "application/json",
            },
        })
        if (response.ok) {

            this.registerForm.reset()
            window.location.href = pageUrl.userPage
            return
        }
        /** @type {ErrorResponse} */
        const error = await response.json()
        if ( !renderTemplateByErrors(error.code, this.pageContainerElement )) {
            showError(this.elemenRegisterError, error)
        }
    }


}

export { AuthService }