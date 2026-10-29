/**
 * @typedef {import('./type.js').ErrorResponse } ErrorResponse
 */


/**
 * @param {HTMLElement} elementError 
 */
function clearError(elementError) {
    elementError.hidden = true
    elementError.replaceChildren()
}

/**
 * @param {HTMLElement} elementError 
 */
function preparationError(elementError) {
    elementError.hidden = false
    elementError.replaceChildren()
}



/**
 * @param {HTMLElement} elementError
 * @param {ErrorResponse} error 
 */
function showError(elementError, error) {
    preparationError(elementError)
    if (Array.isArray(error.message)) {
        error.message.forEach(element => {
            const paragraph = document.createElement("p")
            paragraph.textContent = element["message"]
            elementError.appendChild(paragraph)
        });
    } else {
        const paragraph = document.createElement("p")
        paragraph.textContent = error["message"]
        elementError.appendChild(paragraph)
    }
}


const originError =  {
    code: "ORIGIN ERROR",
    template: document.getElementById("forbidden-template"),
}
const referrError =  {
    code: "REFERER ERROR",
    template: document.getElementById("forbidden-template"),
}
const IpNotFoundError =  {
    code: "IP NOT FOUND",
    template: document.getElementById("internal-server-template"),
}

const errorCode = {
    originError: originError,
    refererError: referrError,
    ipNotFoundError: IpNotFoundError,
}


function renderTemplateByErrors(code,  pageContaier) {
    const list_errors_codes = Object.values(errorCode)
    for (let errorElement of list_errors_codes) {
        if (code === errorElement.code) {
            pageContaier.replaceChildren(
                errorElement.template.content.cloneNode(true)
            )
            return true
        }
    }
    return false
}


export { showError, clearError, errorCode, renderTemplateByErrors}
