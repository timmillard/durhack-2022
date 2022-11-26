//code adapted from: https://dev.to/ara225/how-to-use-bootstrap-modals-without-jquery-3475

function openModal(modal_id) {
    document.getElementById("backdrop").style.display = "block"
    document.getElementById(modal_id).style.display = "block"
    document.getElementById(modal_id).classList.add("show")
}
function closeModal(modal_id) {
    document.getElementById("backdrop").style.display = "none"
    document.getElementById(modal_id).style.display = "none"
    document.getElementById(modal_id).classList.remove("show")
}

// Get the modal
let signup_modal = document.getElementById("sign-up");
signup_modal.addEventListener("click", () => {openModal("sign-up-modal")});

// Get the modal
let signin_modal = document.getElementById("sign-in");
signin_modal.addEventListener("click", () => {openModal("sign-in-modal")});