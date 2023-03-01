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

    const content_type_exists = form.querySelector("#content_type_input")
    if (!content_type_exists) {
        const new_content_type = document.createElement("input")
        new_content_type.id = "content_type_input"
        new_content_type.type = "hidden"
        new_content_type.name = "_content_type"
        new_content_type.value = _content_type
        // noinspection SpellCheckingInspection
        form.insertAdjacentElement("beforeend", new_content_type)
    } else {
        content_type_exists.value = _content_type
    }

    const object_id_exists = form.querySelector("#object_id_input")
    if (!object_id_exists) {
        const new_object_id = document.createElement("input")
        new_object_id.id = "object_id_input"
        new_object_id.type = "hidden"
        new_object_id.name = "_object_id"
        new_object_id.value = _object_id
        // noinspection SpellCheckingInspection
        form.insertAdjacentElement("beforeend", new_object_id)
    } else {
        object_id_exists.value = _object_id
    }
}
