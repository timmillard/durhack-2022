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
let newpost_modal = document.getElementById("pulse-create");
newpost_modal.addEventListener("click", () => { openModal("pulse-create-modal") });

