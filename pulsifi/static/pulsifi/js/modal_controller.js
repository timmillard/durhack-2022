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

function addModalData(modal_id, _content_type, _object_id) {
    const form = document.getElementById(modal_id).querySelector(`#${modal_id} form`)  // TODO: Make form fields in forms.py
    console.log(form)

    // form.querySelector("#creator_id_input").value = creator_id

    form.querySelector("#content_type_input").value = _content_type

    form.querySelector("#object_id_input").value = _object_id
}
